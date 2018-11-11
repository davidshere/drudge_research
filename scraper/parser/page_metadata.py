import collections
import datetime

from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet
import urllib.parse

from drudge_data_classes import DrudgePageMetadata

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com',
  'www.drudgereportarchives.com'
]

LOGO_FILENAME = 'logo9.gif'

NEW_HTML_BEGINS = datetime.datetime(2009, 10, 6, 5, 57, 42)

class ParseError(Exception):
  pass


def find_splash_with_font_size(soup: BeautifulSoup) -> set:
  """ Takes soup and returns the <a> elements representing
      the page splash.

      If no link element is found, returns an empty set
  """
  null_set = set()
  font_size_element = soup.find('font', {"size":"+7"})
  if not font_size_element:
    return null_set

  splash_links_with_text = [link for link in font_size_element.find_all('a') if link.text]
  print("splash links", splash_links_with_text)
  if splash_links_with_text:
    return set(splash_links_with_text)
  else:
    return null_set
  # if the HTML is malformed or the headline isn't a link,
  # this line will return -1
  link = font_size_element.next.find('a')
  if link != -1:
    return null_set

def find_splash_from_center_tag(soup: BeautifulSoup) -> set:
  """ 
  As a backup to find_splash_with_font_size, this method will try to figure
  out the splash based on the center tags. If we can find a single link in
  a center tag, we can (maybe) assume it is a splash
  """
 

# before mid-2009
def is_logo_link(element):
  contents = element.contents
  if len(contents) != 1:
    return False

  tag = contents[0]
  if not isinstance(tag, Tag):
    return False

  src = tag.get('src')
  if not src:
    return False

  return src.split('/')[-1] == LOGO_FILENAME


def index_for_splash_element_in_list_of_links(found_splash, links):
  """ Find the index of the element found_splash in the list of links. """
  if found_splash and found_splash in links:
    splash_index = links.index(found_splash)
  else:
    for index, link in enumerate(links):
      if is_logo_link(link):
        splash_index = index
        break
    else:
      raise ParseError("Couldn't parse metadata for {}, HTML likely malformed.")

  return splash_index


def get_early_top(links: ResultSet, found_splash: set, page_dt: datetime.datetime):
  top_links = set()
  try:
    splash_index = index_for_splash_element_in_list_of_links(found_splash, links)
  except ParseError as e:
    error_message = e.args[0]
    if '{}' in error_message:
      raise ParseError(error_message.format(page_dt))
    else:
      raise

  for link in links[splash_index-1 : 0 : -1]:
    href_netloc = urllib.parse.urlparse(link.get('href')).netloc.lower()

    # empty links
    if not href_netloc:
      continue
    if href_netloc in STOP_DOMAINS:
      return top_links

    if link not in found_splash and link.text:
        top_links.add(link)
    
  raise Exception("wait, I shouldn't be down here")


def early_top_splash_finder(soup: BeautifulSoup, page_dt: datetime.datetime) -> DrudgePageMetadata:
  splash_set = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top_set = get_early_top(links, splash_set, page_dt)
  return DrudgePageMetadata(
    splash_set=splash_set or None,
    top_set=top_set or None
  )


def recent_top_splash_finder(soup: BeautifulSoup, _) -> DrudgePageMetadata:
  """ Parses drudge page metadata from earlier iterations with the drudge report """
  drudge_top_headlines = soup.find('div', {'id': 'drudgeTopHeadlines'})

  if not drudge_top_headlines:
    raise ParseError("id: 'drudgeTopHeadlines' not found")

  splash = find_splash_with_font_size(drudge_top_headlines)

  top_links = drudge_top_headlines.find_all('a')
  if top_links: 
    top_links = set(top_links)
    top_links = top_links.difference(splash)

  return DrudgePageMetadata(
    splash_set=splash or None,
    top_set=top_links or None)


def parse_main_and_splash(soup: BeautifulSoup, page_dt: datetime.datetime) -> DrudgePageMetadata:
  # we've got different parsing methods for earlier and later iterations
  # of the drudge report
  metadata_parser = recent_top_splash_finder if page_dt >= NEW_HTML_BEGINS else early_top_splash_finder
  metadata = metadata_parser(soup, page_dt)
  return metadata 

