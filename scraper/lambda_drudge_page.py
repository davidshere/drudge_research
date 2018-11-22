""" 
Contains functions to run in AWS Lambda, that should take in a date and output all drudge links for that date.

For starters, this lambda will take a drudge page URL, fetch it, parse it, and write the html and parsed links to s3
"""
import datetime

import requests

from html_parser import parser
from drudge_data_classes import DrudgePage

def drudge_page_into_drudge_links(drudge_page):
  html = requests.get(drudge_page.url).text
  return parser.html_into_drudge_links(html, drudge_page.page_dt)

def handler(event, context):
  return drudge_page_into_drudge_links(event['drudge_page'])

if __name__ == "__main__":
  url = 'http://www.drudgereportarchives.com/data/2013/12/18/20131218_010738.htm'
  event = {'drudge_page': DrudgePage(url, datetime.datetime.now())}
  links = handler(event, 'x')
  print('\n'.join([link.to_csv() for link in links]))
