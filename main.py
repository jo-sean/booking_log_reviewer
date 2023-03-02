# Sean Perez
# Collab: Dominic Stewart
# Date: 01/12/2022

from read_excel import read_excel_files
from read_bookings import read_bookings_file
from logic import CalculateChargeableTime, outputBookingDF
from overwrite_excel import overwrite_excel_file


def main():
    # Open security report files
    read_excel_files()

    # Open bookings file
    read_bookings_file()

    # Process the files and calculates times
    CalculateChargeableTime()

    # Outputs the times in csv file
    outputBookingDF()

    # Overwrites the cells in bookings file
    overwrite_excel_file()

if __name__ == "__main__":
    main()