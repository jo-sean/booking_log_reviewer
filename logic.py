import datetime as dt
from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
from workalendar.core import SAT, SUN
import config
import pandas as pd
from pathlib import Path  

timezone = ZoneInfo(config.timezone)
FRIDAY = 4

dayStart = dt.time(8,0,0)
dayEnd = dt.time(16,30,0)

cal = NewZealand()


def CalculateBillableTime():
    config.securityDF[1] = config.securityDF[1].apply(stringToTimestamp)
    getAllTimeDiffList()


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
    config.bookingsDF['ChargeableStart'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableEnd'] = pd.Series(dtype='float64')

    for index, row in config.securityDF.iterrows():
        if len(row['BookingIndex']) > 0:
            if 'open by' in row[5].lower():
                bookingTime = pd.to_datetime(config.bookingsDF['Start'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingTime)                
                setChargeableStartTime(row['BookingIndex'][0], row[1], bookingTime, isWorkingHours)
            elif 'close by' in row[5].lower():
                bookingTime = pd.to_datetime(config.bookingsDF['End'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingTime)
                setChargeableEndTime(row['BookingIndex'][0], row[1], bookingTime, isWorkingHours)

    fillNaN()

    for index, row in config.bookingsDF.iterrows():
        print(f"{index} {row['Activity']}   {row['Location']}")
        print(f"{row['Start']}    {row['ChargeableStart']}")
        print(f"{row['End']}    {row['ChargeableEnd']}")
        print("-------------------------------------------------------")

    filepath = Path('out.csv')  

    filepath.parent.mkdir(parents=True, exist_ok=True) 
    config.bookingsDF[['Activity', 'Location', 'Start', 'End', 'ChargeableStart', 'ChargeableEnd']].to_csv(filepath)

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

def setChargeableStartTime(index, setTime, bookingTime, isWorkingHours):
    timeToSet = bookingTime
    if not isWorkingHours:
        if setTime < bookingTime:
            timeToSet = setTime
        

    config.bookingsDF.loc[index, 'ChargeableStart'] = timeToSet

def setChargeableEndTime(index, setTime, bookingTime, isWorkingHours):
    # If no actual time exists the assign booking time if within working hours
    # Otherwise assign security time
    timeToSet = config.bookingsDF.loc[index, 'ChargeableEnd']
    if pd.isna(config.bookingsDF.loc[index, 'ChargeableEnd']):
        if not isWorkingHours:
            if setTime > bookingTime:
                timeToSet = setTime
        else:
            timeToSet = bookingTime

    config.bookingsDF.loc[index, 'ChargeableEnd'] = timeToSet

def fillNaN():
    config.bookingsDF['ChargeableStart'].fillna(config.bookingsDF['Start'], inplace=True)
    config.bookingsDF['ChargeableEnd'].fillna(config.bookingsDF['End'], inplace=True)