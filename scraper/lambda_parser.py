"""
This module contains a function `handler` that is the main
entry point for an AWS Lambda function. This function will take
a list of pages to parse - either day pages or drudge pages, and
it will parse them.

If it comes across a day page, it will parse it, and post the drudge page
info to the SQS queue. If it comes across a drudge page, it will parse the links,
write them to S3 as a compressed CSV along with the the html and the drudge page
information as a compressed CSV
"""

import datetime
import json
import multiprocessing

import boto3

from drudge_data_classes import DayPage, DrudgePage
import sqs_utils
from html_parser import parser, transform_day_page

def main(page_to_parse):
  if page_to_parse['cls'] == 'day_page':
    day_page = DayPage.from_json(page_to_parse)
    drudge_pages = [page.to_json() for page in transform_day_page.transform_day_page(day_page)]
    print(f"Found {len(drudge_pages)} drudge pages in {page_to_parse['dt']}")
    posted = sqs_utils.post_to_queue(drudge_pages, sqs_utils.fetch_queue)
    return posted
  else:
   raise NotImplementedError("Can't parse Drudge Pages yet")

def handler(event, context):
  page = event['Records'][0]['body']
  return main(page)


if __name__ == "__main__":
  with open('test/resources/20011118_235701.html', 'r') as f:
    drudge_page_html = f.read()
  
  with open("test/resources/test_day_page_1.html", 'r') as f:
    day_page_html = f.read()

  test_day_page_body = {
    'html': day_page_html,
    'dt': datetime.datetime(2017, 8, 12).date(),
    'cls': 'day_page',
    'url': 'http://www.drudgereportarchives.com/data/2018/11/25/index.htm?s=flag'
  }

  test_day_page_event = {
    'Records': [{
      'body': test_day_page_body 
    }]
  }

  print(handler(test_day_page_event, 'x'))
