import datetime as dt
from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
from workalendar.core import SAT, SUN
import event

timezone = ZoneInfo('Pacific/Auckland')
FRIDAY = 4

dayStart = dt.time(8,30,0, tzinfo=timezone)
dayEnd = dt.time(16,0,0, tzinfo=timezone)

cal = NewZealand()


def CalculateBillableTime(event):
    eventStartTime = dt.strptime(event.startTime)
    eventEndTime = dt.strptime(event.endTime)

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
    
    