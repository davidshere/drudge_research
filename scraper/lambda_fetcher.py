"""
This module contains a function `handler` that is the main
entry point for an AWS Lambda function. This function will
take a list of DayPages or DrudgePages, serialized into JSON,
it will asynchronously fetch the html, and will post the result
to an output sink - SQS or Kinesis, it's unclear which
"""
import asyncio
import time

import aiohttp
import boto3

import sqs_utils

test_event = [{
  "url": "http://www.drudgereportarchives.com/data/2018/11/25/index.htm?s=flag",
  "dt": "2018-11-25 11:35:42.732506",
  "cls": "day_page"
}, {
  "url": "http://www.drudgereportarchives.com/data/2018/11/24/index.htm?s=flag",
  "dt": "2018-11-24",
  "cls": "day_page"
}]


async def worker(name, fetch_queue, result_queue):
  page = await fetch_queue.get()

  # await the text of the page, attach it to the object
  # we got the url from, and post it to the result queue
  async with aiohttp.ClientSession() as session:
    async with session.get(page['url']) as resp:
      text = await resp.text()

  # strip control characters
  clean_text = text.translate(dict.fromkeys(range(32)))
  page['html'] = clean_text
  
  result_queue.put_nowait(page)
  fetch_queue.task_done()

async def main(pages):
  # put pages onto async queue
  fetch_queue = asyncio.Queue()
  for page in pages:
    fetch_queue.put_nowait(page)
  
  # instantiate result queue
  result_queue = asyncio.Queue()

  # instantiate workers to handle async calls
  fetch_tasks = []
  for i in range(2):
    task = asyncio.create_task(worker(f'worker-{i}', fetch_queue, result_queue))
    fetch_tasks.append(task)

  # block until the queue is empty
  await fetch_queue.join()

  # cancel running workers
  for task in fetch_tasks:
    task.cancel()

  await asyncio.gather(*fetch_tasks, return_exceptions=True)

  # pull html out of the result queue
  processed_pages = []
  while not result_queue.empty():
    processed_pages.append(result_queue.get_nowait())

  result = sqs_utils.post_to_queue(processed_pages, sqs_utils.parse_queue)
  return result
  

def handler(event, context):
  asyncio.run(main(event))


if __name__ == "__main__":
  handler(test_event, 'y')

