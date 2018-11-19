import collections
import datetime

from bs4 import BeautifulSoup, Tag
import urllib.parse

from drudge_data_classes import DrudgeLink, DrudgePageMetadata
from html_parser import page_metadata
import utils

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com',
  'www.drudgereportarchives.com'
]

LOGO_FILENAME = 'logo9.gif'

# for BeautifulSoup
HTML_PARSER = 'html5lib'

# Datetime that drudge switched to a new html structure
NEW_HTML_BEGINS = datetime.datetime(2009, 10, 6, 5, 57, 42)


def process_link_text(link):
  text = link.text.strip()
  text = text.replace('\n', ' ')
  #if text.endswith('...'):
  #  text = text[:-3]
  return text

def process_raw_link(link: Tag, metadata: DrudgePageMetadata, page_dt: datetime.datetime) -> DrudgeLink:
  """ Uses link and page metadata to transform a link into a DrudgeLink """
  url = link.get('href')

  if url and link.text.strip():
    # determine if the link is in the top or the splash. If top or splash are empty
    # then obviously the link is not a member of the empty set
    splash = link.text in metadata.splash_set if metadata.splash_set else False
    top = link.text in metadata.top_set if metadata.top_set else False

    text = process_link_text(link)

    return DrudgeLink(url, page_dt, text, top, splash)

def soup_into_links_and_metadata(soup: BeautifulSoup, page_dt: datetime.datetime) -> (list, DrudgePageMetadata):
 
  # we want to remove <td> tags with the class "text9"
  utils.remove_dra_tags_from_soup(soup)

  all_links = soup.find_all('a')

  # if there are fewer than 16 links on the page
  # it was likely an error of some kind
  if len(all_links) <= 16:
    return [], DrudgePageMetadata()

  metadata = page_metadata.get_page_metadata(soup, page_dt)
  return all_links, metadata
  

def transform_html(html: str, page_dt: datetime.datetime) -> (list, DrudgePageMetadata):
  soup = BeautifulSoup(html, HTML_PARSER)
  return soup_into_links_and_metadata(soup, page_dt)
  

def html_into_drudge_links(html: str, page_dt: datetime.datetime) -> list:
  """ Main transformation method. """
  all_links, metadata = transform_html(html, page_dt) 

  # We need to loop through the links and create DrudgeLink objects.
  processed_links = []
  for link in all_links:
    drudge_link = process_raw_link(link, metadata, page_dt)
    if drudge_link:
      processed_links.append(drudge_link)

  return processed_links
