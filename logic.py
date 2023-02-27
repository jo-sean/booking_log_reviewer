import datetime as dt
import os
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

gracePeriod = 15

# Calculate the time that can be charged
def CalculateChargeableTime():
    config.securityDF[1] = config.securityDF[1].apply(stringToTimestamp)
    timeDiffList = getAllTimeDiffList()
    prepareBookingDF(timeDiffList)
    parseSecDF()
    parseBookingDF()

# Convert the security report times into a usable format
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

# Get a list of time differences for each booking with the time from the security report
def getAllTimeDiffList():
    timeDiffList = []
    
    for index, row in config.securityDF.iterrows():
        if 'open by' in row[5].lower():          
            timeDiffList.append(getTimeDiffs(row['Room'], row[1], 'Start'))
        elif 'close by' in row[5].lower():         
            timeDiffList.append(getTimeDiffs(row['Room'], row[1], 'End'))
    
    return timeDiffList

# Calculate the time difference for every booking with the time in security report
def getTimeDiffs(room, entryDate, columnName):
    entryTime = entryDate
    entryDate = pd.to_datetime(entryDate.date())

    filteredDf = config.bookingsDF.copy()

    mask = ((filteredDf[columnName] > entryDate) & 
            (filteredDf[columnName] <= (entryDate + pd.Timedelta(days=1))) & 
            (filteredDf['Location'] == room))

    filteredDf.loc[mask, 'TimeDiff'] = (filteredDf[columnName] - entryTime).dt.total_seconds() / 60

    print("-----------------------------")
    print(entryTime)
    print(filteredDf[['Activity', 'Location', columnName]].loc[filteredDf['Location'] == room])

    filteredDf = filteredDf.dropna()

    return filteredDf.loc[(filteredDf['TimeDiff']) == min(filteredDf['TimeDiff'], key=abs, default=0)].index.values

# Create additional columns in bookingDF needed for calculations
def prepareBookingDF(timeDiffList):
    config.securityDF['BookingIndex'] = timeDiffList
    config.bookingsDF['ActualTimes'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableStartDateTime'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableEndDateTime'] = pd.Series(dtype='float64')
    config.bookingsDF['testStart'] = pd.Series(dtype='float64')
    config.bookingsDF['testEnd'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableStart'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableEnd'] = pd.Series(dtype='float64')

# Get bookingDF index of the lowest time difference in security report
def parseSecDF():
    for index, row in config.securityDF.iterrows():
        if len(row['BookingIndex']) > 0:
            if 'open by' in row[5].lower():
                bookingTime = pd.to_datetime(config.bookingsDF['Start'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingTime)
                config.bookingsDF.loc[row['BookingIndex'][0], 'testStart'] = pd.to_datetime(row[1])               
                setActualStartTime(row['BookingIndex'][0], row[1], bookingTime, isWorkingHours)
            elif 'close by' in row[5].lower():
                bookingTime = pd.to_datetime(config.bookingsDF['End'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingTime)
                config.bookingsDF.loc[row['BookingIndex'][0], 'testEnd'] = pd.to_datetime(row[1])
                setActualEndTime(row['BookingIndex'][0], row[1], bookingTime, isWorkingHours)

# If outside working hours sets the ActualStart time to be either the time from the 
# security report or the booking time. 
# If time is less than 15 minutes over uses booking time
def setActualStartTime(index, setTime, bookingTime, isWorkingHours):
    timeToSet = None
    if not isWorkingHours:
        if setTime < bookingTime:
            timeDiff = pd.Timedelta(bookingTime - setTime).seconds / 60
            if timeDiff > gracePeriod:
                setTime = setTime + pd.Timedelta(minutes=gracePeriod)
                timeToSet = setTime
            else:
                timeToSet = bookingTime
    else:
        timeToSet = bookingTime

    config.bookingsDF.loc[index, 'ChargeableStartDateTime'] = timeToSet

# If outside working hours sets the ActualEnd time to be either the time from the 
# security report or the booking time.
# If time is less than 15 minutes over uses booking time
def setActualEndTime(index, setTime, bookingTime, isWorkingHours):
    timeToSet = config.bookingsDF.loc[index, 'ChargeableEndDateTime']
    if pd.isna(timeToSet):
        if not isWorkingHours:
            if setTime > bookingTime:
                timeDiff = pd.Timedelta(setTime - bookingTime).seconds / 60
                if timeDiff > gracePeriod:
                    setTime = setTime - pd.Timedelta(minutes=gracePeriod)
                    timeToSet = setTime
                else:
                    timeToSet = bookingTime 
        else:
            timeToSet = bookingTime

    config.bookingsDF.loc[index, 'ChargeableEndDateTime'] = timeToSet

# Checks if times within working hours
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
    
# Check if the date is a working day (mon-fir and not a public holiday)
def CheckWorkingDay(dateToCheck):
    if dateToCheck.weekday() in {SAT, SUN}:
        print("sat/sun")
        return False

    if CheckPublicHoliday(dateToCheck):
        print("holiday check")
        return False

    return True

# Check if the date is a public holiday
def CheckPublicHoliday(dateToCheck):
    print("test")
    nz_holidays = cal.holidays(dateToCheck.year)
    for holiday in nz_holidays:
        if dateToCheck in holiday:
            return True
    return False

def parseBookingDF():
    fillNaN()
    fillActualTimes()
    fillChargeableTimes()

# Fill NaN entries in actual time with the booking times
def fillNaN():
    config.bookingsDF['ChargeableStartDateTime'].fillna(config.bookingsDF['Start'], inplace=True)
    config.bookingsDF['ChargeableEndDateTime'].fillna(config.bookingsDF['End'], inplace=True)

# Add column with ActualStart/ActualEnd in more a readable HH:MM-HH:MM format
def fillActualTimes():
    for index, row in config.bookingsDF.iterrows():
        actualTimesList = ["...", "..."]
        
        if pd.notna(row['testStart']):
            if pd.notna(row['testEnd']):
                if row['testStart'] < row['testEnd']:
                    actualTimesList[0] = row['testStart'].strftime('%H:%M')
            else:
                actualTimesList[0] = row['testStart'].strftime('%H:%M')
        
        if pd.notna(row['testEnd']):
            actualTimesList[1] = row['testEnd'].strftime('%H:%M')
        config.bookingsDF.loc[index, 'ActualTimes'] = (f"{actualTimesList[0]}-{actualTimesList[1]}")

# Populate ChargeableStart/ChargeableEnd with HH:MM times
def fillChargeableTimes():
    config.bookingsDF['ChargeableStart'] = config.bookingsDF['ChargeableStartDateTime'].dt.strftime('%H:%M')
    config.bookingsDF['ChargeableEnd'] = config.bookingsDF['ChargeableEndDateTime'].dt.strftime('%H:%M')

# Output the necessary information in a csv file
def outputBookingDF():
    os.makedirs('Output_Files', exist_ok=True)
    filename = (f"{config.dateList[0].date()}_to_{config.dateList[-1].date()}")
    filepath = Path(f'Output_Files/bookings_{filename}.csv') 

    config.bookingsDF.set_index(config.bookingsDF.index.values + 2, inplace=True)

    filepath.parent.mkdir(parents=True, exist_ok=True) 
    config.bookingsDF[['Activity', 'Location', 'Start', 'End', 'ActualTimes', 'ChargeableStart', 'ChargeableEnd', 'testStart', 'testEnd', 'ChargeableStartDateTime', 'ChargeableEndDateTime']].to_csv(filepath)
