import datetime as dt
from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
from workalendar.core import SAT, SUN
import config
import pandas as pd

timezone = ZoneInfo('Pacific/Auckland')
FRIDAY = 4

dayStart = dt.time(8,30,0, tzinfo=timezone)
dayEnd = dt.time(16,0,0, tzinfo=timezone)

cal = NewZealand()


def CalculateBillableTime():
    config.securityDF[1] = config.securityDF[1].apply(stringToTimestamp)

    # If entry is open -> list of booking start time differences

    getTimeDeltaList()

    print(config.securityDF)

    # If entry is close -> list of booking end time differences


def CheckPublicHoliday(dateToCheck):
    nz_holidays = cal.holidays(dateToCheck.year)
    for holiday in nz_holidays:
        if dateToCheck in holiday:
            return True
    return False

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

    return pd.Timestamp(pd.to_datetime(f'{dateRange[0]} {dateRange[2]} {dateRange[3]}').strftime('%d-%m-%Y %H:%M:%S'))

def getTimeDeltaList():
    timeDeltaList = []
    
    for index, row in config.securityDF.iterrows():
        if 'open by' in row[5].lower():
            timeDeltaList.append('open')
        elif 'close by' in row[5].lower():
            timeDeltaList.append('close')

    config.securityDF[5] = timeDeltaList    

    # For each code9 entry filter booking times for that room

    # Save index for the booking and time diff for each booking
    # Take the lowest time difference and corresponding index
    # Get the time from the booking index