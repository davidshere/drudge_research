from models import DayPage
from datetime import date, timedelta

BUCKET_NAME = 'drudge-archive'

DAY_PAGE_FMT_URL = "http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag"
START_DATE = date(2001, 11, 18)

def day_pages(start=START_DATE, end=date.today()):
    date_generator = (start + timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        url = DAY_PAGE_FMT_URL % (dt.year, dt.month, dt.day)
        yield DayPage(url, dt)


