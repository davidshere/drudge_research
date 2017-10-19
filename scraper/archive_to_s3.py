import datetime
import io

import boto3
import dateutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import retrying

from models import DayPage, logger

BUCKET_NAME = 'drudge-archive'
S3_LOCATION_FMT = 'data/{yearhalf}.parquet'

START_DATE = datetime.date(2001, 11, 18)
END_DATE = datetime.date.today() - datetime.timedelta(days=1)

@retrying.retry(stop_max_attempt_number=5)
def structured_links_to_s3(links, fname, logger=None):
    df = pd.DataFrame(links)
    arrow_table = pa.Table.from_pandas(df)

    buff = io.BytesIO()
    pq.write_table(arrow_table, buff, flavor='spark')
    buff.seek(0)

    s3 = boto3.resource('s3')

    success = s3.Object(BUCKET_NAME, fname).put(Body=buff)
    if logger:
        logger.info("Wrote to %s", fname)

    return success

def scructured_links_to_disk(links, fname, logger=None):
    df = pd.DataFrame(links)
    pd.to_csv(fname)

def day_pages(start=START_DATE, end=datetime.date.today()):
    date_generator = (start + datetime.timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        yield DayPage(dt)

class ScraperRunner:
    def __init__(self, start_date=START_DATE, end_date=END_DATE, output_fn=structured_links_to_s3):
        self.start_date = start_date
        self.end_date = end_date
        self.current_file = self.dt_to_year_half_str(start_date)
        self.current_links = []
        self.output_fn = output_fn

    def dt_to_year_half_str(self, dt):
        return 'H%dY%d' % ((dt.month - 1) // 6, dt.year)

    def _next_page_is_same_file(self, page):
        return self.dt_to_year_half_str(page.dt + datetime.timedelta(days=1)) == self.current_file

    def _next_page_is_end_date(self, page):
        return page.dt + datetime.timedelta(days=1) == self.end_date

    def run(self):
        for page in day_pages(self.start_date, self.end_date):
            page_links = page.scrape()

            # should the next page be a different file?
            if self._next_page_is_same_file(page) and not self._next_page_is_end_date(page):
                self.current_links.extend(page_links)
            else:
                filename = S3_LOCATION_FMT.format(yearhalf=self.dt_to_year_half_str(page.dt))

                logger.info("Beginning transform of links to parquet and posting to S3 for %s", filename)
                self.output_fn(structured_links_to_s3, self.current_links, filename, logger)
                self.current_links = []
                self.current_file = self.dt_to_year_half_str(page.dt)

if __name__ == "__main__":


    end_date = START_DATE + datetime.timedelta(days=1)
    runner = ScraperRunner(end_date=end_date, output_fn=scructured_links_to_disk)
    runner.run()
