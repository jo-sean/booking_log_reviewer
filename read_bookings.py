import pandas as pd
import os
from get_file import get_file_name
import config


def read_bookings_file():
    """Opens Excel file and extracts contents into dataframe,
    returns two csv files with the totals for users and for rooms"""

    # Column index for the room opening/closing data
    col_index = 5

    # Retrieves name of file being read to be used in the exports

    file_name = get_file_name()
    df = pd.read_excel(file_name, sheet_name='Bookings')
    df = df.astype(str)

    # Retrieves only the file name from the path
    file_name = os.path.splitext(os.path.basename(file_name))[0]

    for i in range(len(config.dateList)):
        config.bookingsDF = pd.concat([config.bookingsDF, df.loc[df['Start'].str.contains(str(config.dateList[i]), case=False) == True]])

    config.bookingsDF['Location'] = config.bookingsDF['Location'].str.lower()
    config.bookingsDF['Start'] = pd.to_datetime(config.bookingsDF['Start'])
    config.bookingsDF['End'] = pd.to_datetime(config.bookingsDF['End'])