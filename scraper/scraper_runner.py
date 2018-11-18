import datetime
import io
import multiprocessing as mp

import asyncio
import aiohttp

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

#from models import DayPage, logger
from drudge_data_classes import DayPage

BUCKET_NAME = 'drudge-archive'
S3_LOCATION_FMT = 'data/{yearhalf}.parquet'

START_DATE = datetime.datetime(2001, 11, 18, 0, 0)
END_DATE = datetime.datetime.combine(datetime.date.today(), datetime.time())


def structured_links_to_s3(links, fname, logger=None):
    logger.info("Beginning transform of links to parquet and posting to S3 for %s", fname)
    df = pd.DataFrame(links)

    arrow_thread_count = mp.cpu_count()
    arrow_table = pa.Table.from_pandas(df, preserve_index=False, nthreads=arrow_thread_count)

    buff = io.BytesIO()
    pq.write_table(arrow_table, buff, flavor='spark')
    buff.seek(0)

    s3 = boto3.resource('s3')

    success = s3.Object(BUCKET_NAME, fname).put(Body=buff)
    if logger:
        logger.info("Wrote to %s", fname)

    return success


def structured_links_to_disk(links, fname, logger=None):
    df = pd.DataFrame(links)
    df.to_csv(fname)


def day_pages(start=START_DATE, end=datetime.date.today()):
    date_generator = (start + datetime.timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        yield DayPage(dt)

def dt_to_year_half_str(dt):
    return 'H%dY%d' % (1 + ((dt.month - 1) // 6), dt.year)

class ScraperRunner:
    def __init__(self, output_fn=structured_links_to_s3):
        self.output_fn = output_fn

    def _increment_file(self, current_page):
        """
        Returns a new file name based on the last DrudgePage of the old
        filename.
        """
        return dt_to_year_half_str(current_page.dt + datetime.timedelta(days=1))

    def _next_page_is_new_file(self, page, filename):
        return dt_to_year_half_str(page.dt + datetime.timedelta(days=1)) != filename

    def _next_page_is_end_date(self, page):
        return page.dt + datetime.timedelta(days=1) == self.end_date

    def _file_is_complete(self, page):
        return self._next_page_is_end_date(page) or self._next_page_is_new_file(page, self.current_file)

    def run(self, start_date=START_DATE, end_date=END_DATE, page_limit=None):
        self.start_date = start_date
        self.end_date = end_date
        self.current_file = dt_to_year_half_str(start_date)

        current_links = []

        for page in day_pages(start_date, end_date):
            print("Fetching %s" % page.dt.isoformat())
            page_links = page.process_day(page_limit=page_limit)
            current_links.extend(page_links)

            # should the next page be a different file?
            if self._file_is_complete(page):
                filename = S3_LOCATION_FMT.format(yearhalf=self.current_file)
                self.output_fn(current_links, filename, logger)

                # reset list of links and expected filename
                current_links = []
                self.current_file = self._increment_file(page)

#### New stuff
import asyncio
import aiohttp

import time

async def worker(name, queue):
  while True:
    drudge_obj_to_fetch =  await queue.get()
    async with aiohttp.ClientSession() as session:
      async with session.get(drudge_obj_to_fetch.url) as resp:
        text = await resp.text()
        drudge_obj_to_fetch.html = text
    queue.task_done()

async def main():

  DAY_PAGE_FETCH_PRIORITY = 2
  DRUDGE_PAGE_FETCH_PRIORITY = 1
  day_pages_to_parse = day_pages(start=(datetime.datetime.now() - datetime.timedelta(days=40)).date())

  start = time.monotonic()
  io_queue = asyncio.Queue()

  for day_page in day_pages_to_parse:
   io_queue.put_nowait(day_page)

  tasks = []
  for i in range(15):
    task = asyncio.create_task(worker(f'worker-{i}', io_queue))
    tasks.append(task)
  
  await io_queue.join()

  for task in tasks:
    task.cancel() 

  await asyncio.gather(*tasks, return_exceptions=True)
  print(time.monotonic() - start)

if __name__ == "__main__":
  asyncio.run(main())









