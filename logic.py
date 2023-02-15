import datetime as dt
from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
from workalendar.core import SAT, SUN
import config
import pandas as pd

timezone = ZoneInfo(config.timezone)
FRIDAY = 4

dayStart = dt.time(8,0,0)
dayEnd = dt.time(16,30,0)

cal = NewZealand()


def CalculateBillableTime():
    config.securityDF[1] = config.securityDF[1].apply(stringToTimestamp)

    # If entry is open -> list of booking start time differences

    getAllTimeDiffList()

    # If entry is close -> list of booking end time differences


def CheckPublicHoliday(dateToCheck):
    nz_holidays = cal.holidays(dateToCheck.year)
    for holiday in nz_holidays:
        if dateToCheck in holiday:
            return True
    return False

def CheckWorkingDay(dateToCheck):
    if dateToCheck.weekday() in {SAT, SUN}:
        return False

    if CheckPublicHoliday(dateToCheck):
        return False

    return True

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

def getAllTimeDiffList():
    timeDiffList = []
    
    for index, row in config.securityDF.iterrows():
        if 'open by' in row[5].lower():          
            timeDiffList.append(getTimeDiffs(row['Room'], row[1], 'Start'))
        elif 'close by' in row[5].lower():         
            timeDiffList.append(getTimeDiffs(row['Room'], row[1], 'End'))

    config.securityDF['BookingIndex'] = timeDiffList
    config.bookingsDF['ActualTimes'] = pd.Series()

    for index, row in config.securityDF.iterrows():
        print(f"{row[1]}        {row['Room']}       {row['BookingIndex']}")
        if len(row['BookingIndex']) > 0:
            if 'open by' in row[5].lower():
                bookingTime = config.bookingsDF['Start'].loc[[row['BookingIndex']][0]].to_string(index=False)
                print(f"Booking start: {bookingTime}")
                print(config.bookingsDF.loc[[row['BookingIndex']][0]].index.values[0])
                print(row['BookingIndex'][0])
                isWorkingHours = validateTimes(row[1])                
                #setActualTime(row['BookingIndex'][0], row[1], bookingTime, isWorkingHours)
            elif 'close by' in row[5].lower():
                if '65522' in row[5]:
                    print("late to close")
                print(f"Booking end: {config.bookingsDF['End'].loc[[row['BookingIndex']][0]].to_string(index=False)}")
                isWorkingHours = validateTimes(row[1])
        print(isWorkingHours)
        print("-------------------------------------------------------")

    print(config.bookingsDF['ActualTimes'].loc[[1352]])
    config.bookingsDF.loc[1352, 'ActualTimes'] = "test"
    print(config.bookingsDF['ActualTimes'].loc[[1352]])

def getTimeDiffs(room, entryDate, columnName):
    entryTime = entryDate
    entryDate = pd.to_datetime(entryDate.date())

    filteredDf = config.bookingsDF.copy()

    mask = ((filteredDf[columnName] > entryDate) & 
            (filteredDf[columnName] <= (entryDate + pd.Timedelta(days=1))) & 
            (filteredDf['Location'] == room))

    filteredDf.loc[mask, 'TimeDiff'] = (filteredDf[columnName] - entryTime).dt.total_seconds() / 60

    filteredDf = filteredDf.dropna()

    return filteredDf.loc[(filteredDf['TimeDiff']) == min(filteredDf['TimeDiff'], key=abs, default=0)].index.values

def validateTimes(entryDate):
    dayStartDateTime = pd.to_datetime(pd.Timestamp.combine(date=entryDate, time=dayStart))
    dayEndDateTime = pd.to_datetime(pd.Timestamp.combine(date=entryDate, time=dayEnd))

    if CheckWorkingDay(entryDate.date()):
        if (entryDate >= dayStartDateTime) & (entryDate <= dayEndDateTime):
            return True
        else:
            return False
    else:
        return False

def setActualTime(index, setTime, bookingTime, isWorkingHours):
    if not isWorkingHours:
        config.bookingsDF['ActualTimes'].loc[[index]] = setTime
    else:
        config.bookingsDF['ActualTimes'].loc[[index]] = bookingTime

    print(f"Actual Time: {config.bookingsDF['ActualTimes'].iloc[[index]]}")