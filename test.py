from zoneinfo import ZoneInfo
from workalendar.oceania import NewZealand
import datetime

ZoneInfo('Pacific/Auckland')

timeNow = datetime.datetime.now()

print(timeNow)

cal = NewZealand()

nz_holidays = cal.holidays(2023)

for x in range(len(nz_holidays)):
    print(nz_holidays[x])
