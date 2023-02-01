import pandas as pd
import os
from get_file import get_file_name


def read_bookings_file():
    """Opens Excel file and extracts contents into dataframe,
    returns two csv files with the totals for users and for rooms"""

    # Column index for the room opening/closing data
    col_index = 5

    # Retrieves name of file being read to be used in the exports

    file_name = get_file_name()
    df = pd.read_excel(file_name, sheet_name=None, header=None)

    # Retrieves only the file name from the path
    file_name = os.path.splitext(os.path.basename(file_name))[0]

    print(df)

    print("Bookings opened")