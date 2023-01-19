import datetime as dt
from zoneinfo import ZoneInfo
import event

timezone = ZoneInfo('Pacific/Auckland')
FRIDAY = 4

dayStart = dt.time(8,30,0, tzinfo=timezone)
dayEnd = dt.time(16,0,0, tzinfo=timezone)


def CalculateBillableTime(event):
    eventStartTime = dt.strptime(event.startTime)
    eventEndTime = dt.strptime(event.endTime)

    ###################################################################################
    #
    # Check sharepoint list for public holiday
    # If date exists in list
    #   publicholiday = True
    #
    # If public holiday or Saturday or Sunday
    #   working hours = null
    # Else
    #   working hours = 08:00, 16:30
    #
    # START TIME LOGIC
    #
    # If event actual start time is within working hours
    #   billable start time = booking start time
    # If event actual start time is outside working hours
    #   If event actual start time is >15mins before booking start time 
    #       billable start time = actual start time
    #   billable start time = booking start time
    #
    # FINISH TIME LOGIC
    #
    # If event actual finish time is within working hours
    #   billable finish time = booking finish time
    # If event actual finish time is outside working hours
    #   If event actual finish time is >15mins before booking finish time
    #       billable finish time = actual finish time
    #   billable finish time = booking finish time
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

    event.startTime = dayEnd # Get time from code9
    event.endTime = dayStart # Get time from code9
