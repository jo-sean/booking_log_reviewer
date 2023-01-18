from O365 import Account, MSGraphProtocol
from zoneinfo import ZoneInfo
import datetime
from event import Event

def minute_diff_from_start_time(event):
    """Returns the time difference from now and the start of the event"""
    now = datetime.datetime.now()
    now = now.strftime('%H:%M:%S')

    event_string = str(event)

    start_index = event_string.find('from:') + 6
    end_index = event_string.find('to:') - 1 
    start_meeting_time = event_string[start_index:end_index]

    start_obj = datetime.datetime.strptime(start_meeting_time, '%H:%M:%S')
    now = datetime.datetime.strptime(now, '%H:%M:%S')

    time_diff_min = ((start_obj - now).total_seconds())/60

    return time_diff_min

ZoneInfo('Pacific/Auckland')

CLIENT_ID = '27a56074-e1f8-406b-b41b-fb4c99cbf612'
SECRET_ID = '5rR8Q~WbL~s-62u1ktRcAuSJCSmtrdgt7_hG8dui'

credentials = (CLIENT_ID, SECRET_ID)

protocol = MSGraphProtocol(defualt_resource='dominic@phillipstown.org.nz') 
scopes = ['Calendars.Read', 'Calendars.Read.Shared']
account = Account(credentials, protocol=protocol)

if account.authenticate(scopes=scopes):
   print('Authenticated!')

schedule = account.schedule()
calendar = schedule.get_default_calendar()

qEventDate = datetime.date.today()
qStartDateTime= datetime.datetime(qEventDate.year, qEventDate.month, qEventDate.day, 0,0,0, tzinfo=ZoneInfo('Pacific/Auckland'))
qEndDateTime= qStartDateTime + datetime.timedelta(days=1)

# Gets the events for the day
q = calendar.new_query('start').greater_equal(qStartDateTime)
q.chain('and').on_attribute('end').less_equal(qEndDateTime)
events = calendar.get_events(query=q, include_recurring=True)

# Displays each event
for event in events:
    eventStringList = str(event).split('(')
    
    # Get event name
    eventName = eventStringList[0].rstrip(' ')
    eventName = eventName.split(':')
    eventName = eventName[1].lstrip(' ')

    # Get event times
    eventDetails = eventStringList[1].split(' ')
    eventDetails[-1] = eventDetails[-1].rstrip(')')
    startTime = datetime.datetime.strptime(f'{eventDetails[1]} {eventDetails[3]}', '%Y-%m-%d %H:%M:%S')
    endTime = datetime.datetime.strptime(f'{eventDetails[1]} {eventDetails[5]}', '%Y-%m-%d %H:%M:%S')

    # Create new event
    newEvent = Event(eventName, startTime, endTime)
    print(f'{newEvent.name} {newEvent.startTime} {newEvent.endTime}')

    startTimeDiff = minute_diff_from_start_time(event)
    print(startTimeDiff)

    # Send event reminder
    if startTimeDiff <= 5 and startTimeDiff >= 0 and newEvent.hasBeenReminded == False:
        newEvent.sendReminder()