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
    config.securityDF["BookingsStartTimes"] = ""
    config.securityDF["BookingsEndTimes"] = ""

    config.securityDF[1] = config.securityDF[1].apply(stringToTimestamp)

    print(config.securityDF)




    ###################################################################################
    #
    # timeRange = [startTime, finishTime]
    # nonWorkingDay = False
    # 
    # CheckAllTimes()
    # CalculateBillableHours()
    # 
    #
    # CheckAllTimes()
    #   For each entry in code9DF find most likely booking
    #   List of time difference between code9 open and booking start
    #   List of time difference between code9 close and booking end
    #   Loop time differences and assign the least time difference as the actual time
    #   If actual time unassigned; assign booking time as actual time
    #
    #
    # CalculateBillableHours()
    #   Check if public holiday
    #   If date exists in list
    #       nonWorkingDay = True
    #   Check if weekend
    #   If weekday > 4
    #       nonWorkingDay = True
    #
    #   For each entry calculate if start time is >15mins earlier than booking
    #   If it is assign actual time as billable
    #   Else assign booking time as billable
    #   For each entry calculate if finish time is >15 later than booking
    #   If it is assign actual time as billable
    #   Else assign booking time as billable
    #
    # BILLABLE TIME LOGIC
    #
    # Time difference billable start time and billable finish time
    #
    ###################################################################################

def FindActualTime(event):
    ###################################################################################
    #
    # for each day
    #   for each open/close
    #      calculate time difference between open/close time and start/end times
    #      assign as actual start/end time for the booking with the lowest difference
    #   if actual start/end and booking start/end > 15mins 
    #      billable start/end = actual start/end
    #   else
    #      billable start/end = booking start/end
    ###################################################################################
    eventStartTime = dt.strptime(event.startTime)
    eventEndTime = dt.strptime(event.endTime)

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
    