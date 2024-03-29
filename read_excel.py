import pandas as pd
import os
from contextlib import ExitStack
from get_file import get_file_name, get_file_names
import config

def read_excel_file():
    """Opens Excel file and extracts contents into dataframe"""
    # Column index for the room opening/closing data
    col_index = 5

    # Rooms to check bookings
    rooms_for_bookings = ['1', '2', '5', '6', '7', '10', '10a']

    # Retrieves name of file being read to be used in the exports
    file_name = get_file_name()
    df = pd.read_excel(file_name, sheet_name=None, header=None)

    # Retrieves only the file name from the path
    file_name = os.path.splitext(os.path.basename(file_name))[0]
        
    for key, value in df.items():
        df_col_2 = value[value[2].str.contains('Colliers|Linwood|Downer', case=False) == True]
        df_col_2 = df_col_2[2].str.split(' - ').str[-1].str.lower()
        df_col_2 = df_col_2.str.replace("room ", "")
        value['Room'] = df_col_2.to_string(buf=None,index=False)

    # Concatenate dataframes in dictionary into a single dataframe
    df = pd.concat(df)

    filtered_df.loc[filtered_df['Room'] == "administration", 'Room'] = "10"

    filtered_df = filtered_df.loc[filtered_df[col_index].str.contains('open by|close by', case=False) == True]
    filtered_df = filtered_df.dropna(axis=1)
    # Keep only rooms from list in dataframe
    filtered_df = filtered_df[filtered_df['Room'].isin(rooms_for_bookings)]
    # Remove late to close from dataframe
    filtered_df = filtered_df[filtered_df[col_index].str.contains("65522")==False]
    # Remove PCCCT from dataframe
    filtered_df = filtered_df[filtered_df[col_index].str.contains("PCCCT")==False]

    filtered_df[1] = filtered_df[1].apply(stringToTimestamp)

    config.dateList = filtered_df[1].map(pd.Timestamp.date).unique()
    config.dateList.sort()

    config.securityDF= filtered_df

def read_excel_files():
    filenames = get_file_names()

    # Column index for the room opening/closing data
    col_index = 5

    # Rooms to check bookings
    rooms_for_bookings = ['1', '2', '5', '6', '7', '10', '10a']
    df_dict = []
    df_list = []

    with ExitStack() as stack:
        files = [
            stack.enter_context(open(filename))
            for filename in filenames
        ]
        for file in files:
            df = pd.read_excel(file.name, sheet_name=None, header=None)
            df_dict.append(df)

    for df in df_dict:
        for key, value in df.items():
            df_col_2 = value[value[2].str.contains('Colliers|Linwood|Downer', case=False) == True]
            df_col_2 = df_col_2[2].str.split(' - ').str[-1].str.lower()
            df_col_2 = df_col_2.str.replace("room ", "")
            value['Room'] = df_col_2.to_string(buf=None,index=False)

        df = pd.concat(df)
        df_list.append(df)

    filtered_df = pd.concat(df_list)

    filtered_df.loc[filtered_df['Room'] == "administration", 'Room'] = "10"

    filtered_df = filtered_df.loc[filtered_df[col_index].str.contains('open by|close by', case=False) == True]
    filtered_df = filtered_df.dropna(axis=1)

    filtered_df[1] = filtered_df[1].apply(stringToTimestamp)

    config.dateList = filtered_df[1].map(pd.Timestamp.date).unique()
    config.dateList.sort()

    # Keep only rooms from list in dataframe
    filtered_df = filtered_df[filtered_df['Room'].isin(rooms_for_bookings)]
    # Remove late to close from dataframe
    filtered_df = filtered_df[filtered_df[col_index].str.contains("65522")==False]
    # Remove PCCCT from dataframe
    filtered_df = filtered_df[filtered_df[col_index].str.contains("PCCCT")==False]

    config.securityDF= filtered_df

def stringToTimestamp(string):
    dateRange = string.split(' ')        

    dateRange[0] = dateRange[0].split('/')
    for i in range(len(dateRange[0])):
        if len(dateRange[0][i]) < 2:
            dateRange[0][i] = f'0{dateRange[0][i]}'
    dateRange[0] = f'{dateRange[0][0]}-{dateRange[0][1]}-{dateRange[0][2]}'

    dateRange[2] = dateRange[2].split(':')
    for i in range(len(dateRange[2])):
        if len(dateRange[2][i]) < 2:
            dateRange[2][i] = f'0{dateRange[2][i]}'
    dateRange[2] = f'{dateRange[2][0]}:{dateRange[2][1]}:{dateRange[2][2]}'

    if 'a' in dateRange[3] or 'A' in dateRange[3]:
        dateRange[3] = 'AM'
    else:
        dateRange[3] = 'PM' 

    return pd.to_datetime(f'{dateRange[0]} {dateRange[2]} {dateRange[3]}', format='%d-%m-%Y %I:%M:%S %p')