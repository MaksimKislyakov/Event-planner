from datetime import datetime, timedelta, date
import calendar
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

def get_month_dates(year, month):
    cal = calendar.Calendar()
    month_days = cal.itermonthdays2(year, month) 
    dates = []
    for day, weekday in month_days:
        if day == 0:
            dates.append(None) 
        else:
            dates.append(date(year, month, day))
    return dates

def get_week_dates(start_date):
    start = start_date - timedelta(days=start_date.weekday()) 
    return [start + timedelta(days=i) for i in range(7)]

def get_day_date(day_date):
    return [day_date]
