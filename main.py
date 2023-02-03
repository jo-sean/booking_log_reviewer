# Sean Perez
# Collab: Dominic Stewart
# Date: 01/12/2022

import config
from read_excel import read_excel_file
from read_bookings import read_bookings_file
from logic import CalculateBillableTime


def main():
    read_excel_file()
    read_bookings_file()
    CalculateBillableTime()

if __name__ == "__main__":
    main()