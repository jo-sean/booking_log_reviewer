import pandas as pd
import os
from get_file import get_file_name
import config

def read_excel_file():
    """Opens Excel file and extracts contents into dataframe,
    returns two csv files with the totals for users and for rooms"""

    # Column index for the room opening/closing data
    col_index = 5

    # Rooms to check bookings
    rooms_for_bookings = ['1', '2', '5', '6', '7', '10', '10a']

    # Retrieves name of file being read to be used in the exports

    file_name = get_file_name()
    df = pd.read_excel(file_name, sheet_name=None, header=None)

    # Retrieves only the file name from the path
    file_name = os.path.splitext(os.path.basename(file_name))[0]

    # Get the dates included in the security report
    keylist = list(df.keys())
    dateRange = df[keylist[0]].loc[df[keylist[0]][1].str.contains('From', case=False) == True][1].iat[0]
    dateRange = dateRange.split(' ')

    dateRange[1] = dateRange[1].split('/')
    for i in range(len(dateRange[1])):
        if len(dateRange[1][i]) < 2:
            dateRange[1][i] = f'0{dateRange[1][i]}'
    dateRange[1] = f'{dateRange[1][0]}-{dateRange[1][1]}-{dateRange[1][2]}'

    dateRange[2] = dateRange[2].split(':')
    for i in range(len(dateRange[2])):
        if len(dateRange[2][i]) < 2:
            dateRange[2][i] = f'0{dateRange[2][i]}'
    dateRange[2] = f'{dateRange[2][0]}:{dateRange[2][1]}:{dateRange[2][2]}'
    
    if 'a' or 'A' in dateRange[3]:
        dateRange[3] = 'AM'
    else:
        dateRange[3] = 'PM'    

    startDate = pd.Timestamp(f"{dateRange[1]} {dateRange[2]} {dateRange[3]}", day)
    print(startDate)
    print(f"{dateRange[1]}")

    for i in range(8):
        config.dateList.append(startDate)
        startDate = startDate + pd.DateOffset(days=1)
        
    for key, value in df.items():
        df_col_2 = value[value[2].str.contains('Colliers|Linwood', case=False) == True]
        df_col_2 = df_col_2[2].str.split(' - ').str[-1].str.lower()
        df_col_2 = df_col_2.str.replace("room ", "")
        value['Room'] = df_col_2.to_string(buf=None,index=False)
    
    print(config.dateList)

    # Concatenate dataframes in dictionary into a single dataframe
    df = pd.concat(df)

    filtered_df = df.loc[df[col_index].str.contains('open by|close by', case=False) == True]
    filtered_df = filtered_df.dropna(axis=1)
    filtered_df = filtered_df[filtered_df['Room'].isin(rooms_for_bookings)]
    # Filter out late to closes
    filtered_df = filtered_df[filtered_df[col_index].str.contains("65522")==False]
    #Filter out PCCCT
    filtered_df = filtered_df[filtered_df[col_index].str.contains("PCCCT")==False]
    config.securityDF= filtered_df

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
