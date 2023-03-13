from win32com.client import Dispatch
import os
import config
import datetime
import shutil

def overwrite_excel_file():
    # Fill NaN with white space otherwise displays in excel as 65535
    config.bookingsDF = config.bookingsDF.fillna(' ')

    # Make a copy of the bookings Spreadsheet with timestamped name
    file_name = os.path.splitext(os.path.basename(config.bookingsFile))[0]
    file_path = os.path.dirname(config.bookingsFile)
    now = str(datetime.datetime.now())[:19]
    now = now.replace(":","_")
    file_extension = os.path.splitext(os.path.basename(config.bookingsFile))[1]
    backup_file = f"{file_path}/{file_name}_{str(now)}{file_extension}"
    shutil.copy(config.bookingsFile, backup_file)

    # Open Excel
    xl = Dispatch("Excel.Application")
    xl.Visible = True # otherwise excel is hidden

    wbs_name = config.bookingsFile
    wb = xl.Workbooks.Open(wbs_name)
    sh = wb.Worksheets("Bookings")

    # Get the excel column letters
    actualTimeColumn = pos_to_char(config.bookingsDF.columns.get_loc('Actual Time')).upper()
    chargeableStartColumn = pos_to_char(config.bookingsDF.columns.get_loc('Chargeable Start')).upper()
    chargeableEndColumn = pos_to_char(config.bookingsDF.columns.get_loc('Chargeable End')).upper()
    startRow = config.bookingsDF.index[0]

    # Overwrite the cell values with the value from the dataframe
    for i in range(startRow, (startRow + len(config.bookingsDF))):
        sh.Range(f"{actualTimeColumn}{i}").Value = config.bookingsDF.loc[i]['ActualTimes']
        sh.Range(f"{chargeableStartColumn}{i}").Value = config.bookingsDF.loc[i]['ChargeableStart']
        sh.Range(f"{chargeableEndColumn}{i}").Value = config.bookingsDF.loc[i]['ChargeableEnd']    
    wb.Save()

# Convert a number to a letter
def pos_to_char(pos):
    return chr(pos + 97)