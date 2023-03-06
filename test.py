from win32com.client import Dispatch
import os
import config
import datetime
import shutil

def overwrite_excel_file():

    config.bookingsDF = config.bookingsDF.fillna(' ')

    file_name = os.path.splitext(os.path.basename(config.bookingsFile))[0]
    file_path = os.path.dirname(config.bookingsFile)
    now = str(datetime.datetime.now())[:19]
    now = now.replace(":","_")
    file_extension = os.path.splitext(os.path.basename(config.bookingsFile))[1]
    backup_file = f"{file_path}/{file_name}_{str(now)}{file_extension}"
    print(backup_file)
    shutil.copy(config.bookingsFile, backup_file)

    xl = Dispatch("Excel.Application")
    xl.Visible = True # otherwise excel is hidden

    # newest excel does not accept forward slash in path

    wbs_name = config.bookingsFile
    wb = xl.Workbooks.Open(wbs_name)
    sh = wb.Worksheets("Bookings")

    actualTimeColumn = pos_to_char(config.bookingsDF.columns.get_loc('Actual Time')).upper()
    chargeableStartColumn = pos_to_char(config.bookingsDF.columns.get_loc('Chargeable Start')).upper()
    chargeableEndColumn = pos_to_char(config.bookingsDF.columns.get_loc('Chargeable End')).upper()
    startRow = config.bookingsDF.index[0]

    for i in range(startRow, len(config.bookingsDF)):
        sh.Range(f"{actualTimeColumn}{i}").Value = config.bookingsDF.loc[i]['ActualTimes']
        sh.Range(f"{chargeableStartColumn}{i}").Value = config.bookingsDF.loc[i]['ChargeableStart']
        sh.Range(f"{chargeableEndColumn}{i}").Value = config.bookingsDF.loc[i]['ChargeableEnd']
    wb.Save()

def pos_to_char(pos):
    return chr(pos + 97)