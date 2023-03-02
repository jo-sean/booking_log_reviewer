# Sean Perez
# Collab: Dominic Stewart
# Date: 01/12/2022

import config
from read_excel import read_excel_files
from read_bookings import read_bookings_file
from logic import CalculateChargeableTime, outputBookingDF
from test import overwrite_excel_file


def main():
    read_excel_files()
    read_bookings_file()
    CalculateChargeableTime()
    outputBookingDF()
    overwrite_excel_file()

if __name__ == "__main__":
    main()