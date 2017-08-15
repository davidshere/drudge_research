import datetime
import io

import boto3
import dateutil

from models import DayPage


BUCKET_NAME = 'drudge-archive'
S3_LOCATION_FMT = '/data/{year}/{month}/{day}/{year}{month}{day}.csv'

START_DATE = datetime.date(2001, 11, 18)

def day_pages(start=START_DATE, end=datetime.date.today()):
    date_generator = (start + datetime.timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        yield DayPage(dt)

if __name__ == "__main__":
    start = datetime.datetime.now()
    dt = datetime.date.today() - datetime.timedelta(days=1)
    dp = DayPage(dt)
    links = []
    for page in day_pages(START_DATE, START_DATE + dateutil.relativedelta.relativedelta(months=1)):
        print(page.url)
        page_links = dp.scrape()
        for link in page_links:
            for item in link.get_links():
                links.append(item)

    s3 = boto3.resource('s3')
    f = io.BytesIO(b'\n'.join([b'\t'.join([a for a in l]) for l in links]))
    s3.Object(BUCKET_NAME, 'data/2017/08/20170813.csv').put(Body=f)