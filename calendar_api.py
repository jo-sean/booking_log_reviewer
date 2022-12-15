from O365 import Account, MSGraphProtocol
import datetime
from event import Event



def minute_diff_from_start_time(event):
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

q = calendar.new_query('start').greater_equal(datetime.date.today())
q.chain('and').on_attribute('end').less_equal(datetime.date.today() + datetime.timedelta(days=1))

events = calendar.get_events(query=q, include_recurring=True) 

for event in events:
    print(event)
    eventStringList = str(event).split(' ')
    name = eventStringList[1]
    eventStringList[7] = eventStringList[7].rstrip(')')
    startTime = datetime.datetime.strptime(f'{eventStringList[3]} {eventStringList[5]}', '%Y-%m-%d %H:%M:%S')
    endTime = datetime.datetime.strptime(f'{eventStringList[3]} {eventStringList[7]}', '%Y-%m-%d %H:%M:%S')
    newEvent = Event(name, startTime, endTime)
    print(f'{newEvent.name} {newEvent.startTime} {newEvent.endTime}')
    if minute_diff_from_start_time(event) <= 5 and minute_diff_from_start_time(event) >= 0:
        newEvent.sendReminder()