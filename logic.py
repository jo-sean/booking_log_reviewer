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
    timeDiffList = getAllTimeDiffList()
    prepareBookingDF(timeDiffList)
    parseSecDF()
    parseBookingDF()

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

    filteredDf = filteredDf.dropna()

    return filteredDf.loc[(filteredDf['TimeDiff']) == min(filteredDf['TimeDiff'], key=abs, default=0)].index.values

# Create additional columns in bookingDF needed for calculations
def prepareBookingDF(timeDiffList):
    config.securityDF['BookingIndex'] = timeDiffList
    config.bookingsDF['ActualTimes'] = pd.Series(dtype='float64')
    config.bookingsDF['ActualStart'] = pd.Series(dtype='float64')
    config.bookingsDF['ActualEnd'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableStart'] = pd.Series(dtype='float64')
    config.bookingsDF['ChargeableEnd'] = pd.Series(dtype='float64')

# Get bookingDF index of the lowest time difference in security report
def parseSecDF():
    for index, row in config.securityDF.iterrows():
        if len(row['BookingIndex']) > 0:
            if 'open by' in row[5].lower():
                bookingStartTime = pd.to_datetime(config.bookingsDF['Start'].loc[[row['BookingIndex']][0]].to_string(index=False))
                bookingEndTime = pd.to_datetime(config.bookingsDF['End'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingStartTime)
                config.bookingsDF.loc[row['BookingIndex'][0], 'ActualStart'] = pd.to_datetime(row[1])  
                setActualStartTime(row['BookingIndex'][0], row[1], bookingEndTime, isWorkingHours)             
                setChargeableStartTime(row['BookingIndex'][0], row[1], bookingStartTime, bookingEndTime, isWorkingHours)
            elif 'close by' in row[5].lower():
                bookingStartTime = pd.to_datetime(config.bookingsDF['Start'].loc[[row['BookingIndex']][0]].to_string(index=False))
                bookingEndTime = pd.to_datetime(config.bookingsDF['End'].loc[[row['BookingIndex']][0]].to_string(index=False))
                isWorkingHours = validateTimes(bookingStartTime)
                setActualEndTime(row['BookingIndex'][0], row[1], bookingStartTime, isWorkingHours)
                setChargeableEndTime(row['BookingIndex'][0], row[1], bookingStartTime, bookingEndTime, isWorkingHours)

# If outside working hours sets the ActualStart time to be either the time from the 
# security report or leaves empty 
def setActualStartTime(index, setTime, bookingEndTime, isWorkingHours):
    timeToSet = config.bookingsDF.loc[index, 'ActualStart']

    if pd.isna(timeToSet) and (setTime < bookingEndTime):
        if not isWorkingHours:
            timeToSet = setTime

    config.bookingsDF.loc[index, 'ActualStart'] = timeToSet

# If outside working hours sets the ActualEnd time to be either the time from the 
# security report or leaves empty
def setActualEndTime(index, setTime, bookingStartTime, isWorkingHours):
    timeToSet = config.bookingsDF.loc[index, 'ActualEnd']

    if (pd.isna(timeToSet)) and (setTime > bookingStartTime):
        if not isWorkingHours:
            timeToSet = setTime

    config.bookingsDF.loc[index, 'ActualEnd'] = timeToSet

    
# If outside working hours sets the ChargeableStart time to be either the time from the 
# security report or the booking time. 
# If time is less than 15 minutes over uses booking time
def setChargeableStartTime(index, setTime, bookingStartTime, bookingEndTime, isWorkingHours):
    timeToSet = config.bookingsDF.loc[index, 'ChargeableStart']

    if pd.isna(timeToSet) and (setTime < bookingEndTime):
        if not isWorkingHours:
            if setTime < bookingStartTime:
                timeDiff = pd.Timedelta(bookingStartTime - setTime).seconds / 60
                if timeDiff > gracePeriod:
                    setTime = setTime + pd.Timedelta(minutes=gracePeriod)
                    timeToSet = setTime
                else:
                    timeToSet = bookingStartTime
        else:
            timeToSet = bookingStartTime
    elif setTime < bookingEndTime:
        if setTime < bookingStartTime:
                timeDiff = pd.Timedelta(bookingStartTime - setTime).seconds / 60
                if timeDiff > gracePeriod:
                    setTime = setTime + pd.Timedelta(minutes=gracePeriod)
                    if pd.Timedelta(bookingStartTime - setTime) < pd.Timedelta(bookingStartTime - timeToSet):
                        timeToSet = setTime
                else:
                    timeToSet = bookingStartTime

    config.bookingsDF.loc[index, 'ChargeableStart'] = timeToSet

# If outside working hours sets the ChargeableEnd time to be either the time from the 
# security report or the booking time.
# If time is less than 15 minutes over uses booking time
def setChargeableEndTime(index, setTime, bookingStartTime, bookingEndTime, isWorkingHours):
    timeToSet = config.bookingsDF.loc[index, 'ChargeableEnd']

    if pd.isna(timeToSet) and (setTime > bookingStartTime):
        if not isWorkingHours:
            if setTime > bookingEndTime:
                timeDiff = pd.Timedelta(setTime - bookingEndTime).seconds / 60
                if timeDiff > gracePeriod:
                    setTime = setTime - pd.Timedelta(minutes=gracePeriod)
                    timeToSet = setTime
                else:
                    timeToSet = bookingEndTime 
        else:
            timeToSet = bookingEndTime
    elif setTime > bookingStartTime:
        if setTime < bookingEndTime:
                timeDiff = pd.Timedelta(setTime - bookingEndTime).seconds / 60
                if timeDiff > gracePeriod:
                    setTime = setTime + pd.Timedelta(minutes=gracePeriod)
                    if pd.Timedelta(bookingEndTime - setTime) < pd.Timedelta(bookingEndTime - timeToSet):
                        timeToSet = setTime
                else:
                    timeToSet = bookingEndTime

    config.bookingsDF.loc[index, 'ChargeableEnd'] = timeToSet

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
        return False

    if CheckPublicHoliday(dateToCheck):
        return False

    return True

# Check if the date is a public holiday
def CheckPublicHoliday(dateToCheck):
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
    config.bookingsDF['ChargeableStart'].fillna(config.bookingsDF['Start'], inplace=True)
    config.bookingsDF['ChargeableEnd'].fillna(config.bookingsDF['End'], inplace=True)

# Add column with ActualStart/ActualEnd in more a readable HH:MM-HH:MM format
def fillActualTimes():
    for index, row in config.bookingsDF.iterrows():
        # Checks if ActualStart is before ActualEnd then sets times if it is
        # If no ActualEnd will check if ActualStart is before booking end
        # ActualTime is left as ... if no ActualStart/ActualEnd or the time is invalid 
        actualTimesList = [None, None]

        if pd.notna(row['ActualStart']):
            if pd.notna(row['ActualEnd']):
                if row['ActualStart'] < row['ActualEnd']:
                    actualTimesList[0] = row['ActualStart'].strftime('%H:%M')
            elif row['ActualStart'] < row['End']:
                actualTimesList[0] = row['ActualStart'].strftime('%H:%M')
        
        if pd.notna(row['ActualEnd']):
            actualTimesList[1] = row['ActualEnd'].strftime('%H:%M')

        if pd.notna(actualTimesList[0]) and pd.notna(actualTimesList[1]):
            config.bookingsDF.loc[index, 'ActualTimes'] = (f"{actualTimesList[0]}-{actualTimesList[1]}")
        elif pd.notna(actualTimesList[0]):
            config.bookingsDF.loc[index, 'ActualTimes'] = (f"{actualTimesList[0]}-...")
        elif pd.notna(actualTimesList[1]):
            config.bookingsDF.loc[index, 'ActualTimes'] = (f"...-{actualTimesList[1]}")

# Convert ChargeableStart/ChargeableEnd with HH:MM times
def fillChargeableTimes():
    config.bookingsDF['ChargeableStart'] = config.bookingsDF['ChargeableStart'].dt.strftime('%H:%M')
    config.bookingsDF['ChargeableEnd'] = config.bookingsDF['ChargeableEnd'].dt.strftime('%H:%M')

# Output the necessary information in a csv file
def outputBookingDF():
    os.makedirs('Output_Files', exist_ok=True)
    filename = (f"{config.dateList[0]}_to_{config.dateList[-1]}")
    filepath = Path(f'Output_Files/bookings_{filename}.csv') 

    config.bookingsDF.set_index(config.bookingsDF.index.values + 2, inplace=True)

    filepath.parent.mkdir(parents=True, exist_ok=True) 
    config.bookingsDF = config.bookingsDF.sort_index()
    config.bookingsDF[['Activity', 'Location', 'Start', 'End', 'ActualTimes', 'ChargeableStart', 'ChargeableEnd']].to_csv(filepath)
