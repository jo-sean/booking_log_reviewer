import datetime as dt
from zoneinfo import ZoneInfo
import event

timezone = ZoneInfo('Pacific/Auckland')
FRIDAY = 4

dayStart = dt.time(8,30,0, tzinfo=timezone)
dayEnd = dt.time(16,0,0, tzinfo=timezone)


def CalculateActualTime(event):
    eventStartTime = dt.strptime(event.startTime)
    eventEndTime = dt.strptime(event.endTime)

    # If time is before working hours use code9 times
    if eventStartTime < dayStart or eventStartTime > dayEnd:
        FindActualTime(event)

    # If time is after working hours use code9 times
    if eventEndTime < dayStart or eventEndTime > dayEnd:
        FindActualTime(event)

    # If day is Saturday or Sunday use code9 times
    if eventStartTime.weekday() > FRIDAY:
        FindActualTime(event)

def FindActualTime(event):
    ###################################################################################
    # all day sat sun
    # mon-fri before 08:00 and after 16:00 
    #
    # for each open/close
    #    calculate time difference between open/cloe time and start/end times
    #    assign as actual start/end time for the booking with the lowest difference
    # if actual start/end and booking start/end > 15mins 
    #    billable start/end = actual start/end
    # else
    #    billable start/end = booking start/end
    ###################################################################################

    event.startTime = dayEnd # Get time from code9
    event.endTime = dayStart # Get time from code9
