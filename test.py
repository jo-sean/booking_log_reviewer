import datetime as dt
from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
from workalendar.core import SAT, SUN
import config

timezone = ZoneInfo(config.timezone)
FRIDAY = 4

dayStart = dt.time(8,0,0)
dayEnd = dt.time(16,30,0)

cal = NewZealand()

nz_holidays = cal.holidays(2023)
for holiday in nz_holidays:
    datetest = dt.date(2023,1,2)
    if datetest in holiday:
        print(holiday)