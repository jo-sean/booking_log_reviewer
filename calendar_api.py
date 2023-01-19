from O365 import Account, MSGraphProtocol
from zoneinfo import ZoneInfo
import datetime
from event import Event

timezone = ZoneInfo('Pacific/Auckland')

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
qStartDateTime= datetime.datetime(qEventDate.year, qEventDate.month, qEventDate.day, 0,0,0, tzinfo=timezone)
qEndDateTime= qStartDateTime + datetime.timedelta(days=1)

# Gets the events for the day
q = calendar.new_query('start').greater_equal(qStartDateTime)
q.chain('and').on_attribute('end').less_equal(qEndDateTime)
events = calendar.get_events(query=q, include_recurring=True)

eventsToday = []

# Displays each event
for event in events:
    print(event.body)
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
    eventsToday.append(newEvent)