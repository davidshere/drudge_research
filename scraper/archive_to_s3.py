from models import DayPage
from datetime import date, timedelta

BUCKET_NAME = 'drudge-archive'

START_DATE = date(2001, 11, 18)

def day_pages(start=START_DATE, end=date.today()):
    date_generator = (start + timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        yield DayPage(dt)


