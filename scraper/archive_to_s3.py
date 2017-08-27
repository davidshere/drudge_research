import datetime
import io

import boto3
import dateutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from models import DayPage

BUCKET_NAME = 'drudge-archive'
S3_LOCATION_FMT = '/data/{year}/{month}/{day}/{year}{month}{day}.csv'

START_DATE = datetime.date(2001, 11, 18)


def structured_links_to_s3(links):
    df = pd.DataFrame(links)
    df.to_csv('quarter_test.csv')
    arrow_table = pa.Table.from_pandas(df)

    buff = io.BytesIO()
    pq.write_table(arrow_table, buff)
    buff.seek(0)

    s3 = boto3.resource('s3')
    s3.Object(BUCKET_NAME, 'quarter_test.parquet').put(Body=buff)

def day_pages(start=START_DATE, end=datetime.date.today()):
    date_generator = (start + datetime.timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        yield DayPage(dt)

if __name__ == "__main__":

    links = []
    for page in day_pages(START_DATE, START_DATE + dateutil.relativedelta.relativedelta(months=3)):
        print(page.url)
        page_links = page.scrape()
        links.extend(page_links)

    structured_links_to_s3(links)

    print(len(links))


