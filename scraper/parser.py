import collections
import datetime

from bs4 import BeautifulSoup, Tag
import urllib.parse

from drudge_data_classes import DrudgeLink
import page_metadata

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com',
  'www.drudgereportarchives.com'
]

LOGO_FILENAME = 'logo9.gif'

NEW_HTML_BEGINS = datetime.datetime(2009, 10, 6, 5, 57, 42)

def process_raw_link(link, page_main_links, page_dt):
  url = link.get('href')
  if url:
    # determine if the link is in the top or the splash
    splash = link == page_main_links['splash']
    top = link in page_main_links['top']

    return DrudgeLink(url, page_dt, link.text, top, splash)

def transform_page_into_drudge_links(soup, page_dt):
  """ Main transformation method. """
  all_links = soup.find_all('a')

  # if there are fewer than 16 links on the page
  # it was likely an error of some kind
  if len(all_links) <= 16:
    return []
    raise ParseError("Not enough links on archive page for {}".format(page_dt))

  metadata = page_metadata.get_page_metadata(soup, page_dt)

  # We need to loop through the links and create DrudgeLink objects.
  processed_links = []
  for link in all_links:

    drudge_link = process_raw_link(link, metadata, page_dt)

    if drudge_link:
      processed_links.append(drudge_link)

  return processed_links
