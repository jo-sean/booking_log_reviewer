import pandas as pd
import os
from get_file import get_file_name


def read_excel_file():
    """Opens Excel file and extracts contents into dataframe,
    returns two csv files with the totals for users and for rooms"""

    # Column index for the room opening/closing data
    col_index = 5

    # Retrieves name of file being read to be used in the exports

    file_name = get_file_name()
    df = pd.read_excel(file_name, sheet_name=None, header=None)

    # Retrieves only the file name from the path
    file_name = os.path.splitext(os.path.basename(file_name))[0]

    # Get date range from code9 report 

    for key, value in df.items():
        df_col_2 = value[value[2].str.contains('Colliers|Linwood', case=False) == True]
        df_col_2 = df_col_2[2].str.split(' - ').str[-1]
        value['Room'] = df_col_2.to_string(buf=None,index=False)

    # Concatenate dataframes in dictionary into a single dataframe
    df = pd.concat(df)

    filtered_df = df.loc[df[col_index].str.contains('open by|close by', case=False) == True]
    filtered_df = filtered_df.dropna(axis=1)


    # # String manipulation
    # totals_user_id, totals_room_num = loop_dp(filtered_df)

    # Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    # Convert to dataframes
    # df1 = pd.DataFrame.from_dict(totals_user_id, orient="index")
    # df2 = pd.DataFrame.from_dict(totals_room_num, orient="index")

    # Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    # Source: https://pandas.pydata.org/pandas-docs/version/0.7.0/generated/pandas.DataFrame.to_csv.html
    # os.makedirs('Output Files', exist_ok=True)
    # df1.to_csv(f'Output Files/totals_per_user_{file_name}.csv',
    #            index_label=['User ID'],
    #            header=['Total Time Used'])
    # df2.to_csv(f'Output Files/totals_per_room_{file_name}.csv',
    #            index_label=['Room Number'],
    #            header=['Total Time Used'])
