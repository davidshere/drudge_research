import collections
import datetime

from bs4 import BeautifulSoup, Tag
import urllib.parse

from drudge_data_classes import DrudgeLink, DrudgePageMetadata
from html_parser import page_metadata

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com',
  'www.drudgereportarchives.com'
]

LOGO_FILENAME = 'logo9.gif'

NEW_HTML_BEGINS = datetime.datetime(2009, 10, 6, 5, 57, 42)

def process_raw_link(link: str, metadata: DrudgePageMetadata, page_dt: datetime.datetime) -> DrudgeLink:
  """ Uses link and page metadata to transform a link into a DrudgeLink """
  url = link.get('href')
  if url:
    # determine if the link is in the top or the splash. If top or splash are empty
    # then obviously the link is not a member of the empty set
    splash = link.text in metadata.splash_set if metadata.splash_set else False
    top = link.text in metadata.top_set if metadata.top_set else False

    return DrudgeLink(url, page_dt, link.text, top, splash)

def soup_into_links_and_metadata(soup: BeautifulSoup, page_dt: datetime.datetime) -> (list, DrudgePageMetadata):
  
  all_links = soup.find_all('a')

  # if there are fewer than 16 links on the page
  # it was likely an error of some kind
  if len(all_links) <= 16:
    return [], DrudgePageMetadata()
    raise page_metadata.ParseError("Not enough links on archive page for {}".format(page_dt))

  metadata = page_metadata.get_page_metadata(soup, page_dt)
  return all_links, metadata
  

def transform_html_with_parser(html: str, parser: str, page_dt: datetime.datetime) -> (list, DrudgePageMetadata):
  soup = BeautifulSoup(html, parser)
  return soup_into_links_and_metadata(soup, page_dt)
  

def html_into_drudge_links(html: str, page_dt: datetime.datetime) -> list:
  """ Main transformation method. """
  try:
    all_links, metadata = transform_html_with_parser(html, "lxml", page_dt) 
  except page_metadata.ParseError as pe:
    # try to parse again with a different parser, as a backup
    all_links, metadata = transform_html_with_parser(soup, "html5lib", page_dt)

  # We need to loop through the links and create DrudgeLink objects.
  processed_links = []
  for link in all_links:
    drudge_link = process_raw_link(link, metadata, page_dt)

    if drudge_link:
      processed_links.append(drudge_link)

  return processed_links
