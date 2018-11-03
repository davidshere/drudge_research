import collections
import datetime

from bs4 import BeautifulSoup, Tag
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


def find_splash_with_font_size(soup):
  """ Takes soup and returns the <a> elements representing
      the page splash.

      If no link element is found, returns None
  """
  font_size_element = soup.find('font', {"size":"+7"})
  if not font_size_element:
    return None

  splash_links = font_size_element.find_all('a')
  if splash_links:
    return set(splash_links)

  # if the HTML is malformed or the headline isn't a link,
  # this line will return -1
  link = font_size_element.next.find('a')
  if link != -1:
    print("here!", set([link]))
  
    return None 


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


def get_early_top(links, found_splash, page_dt):
  found_splash = found_splash 
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
    if href_netloc in STOP_DOMAINS:
      return None 

    if found_splash and link.text and link not in found_splash:
      top_links.add(link)
  raise ParseError("get_early_top returned None - it shouldn't do that")


def early_top_splash_finder(soup, page_dt):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_early_top(links, splash, page_dt)
  return DrudgePageMetadata(splash_set=splash, top_set=top)


# going back to mid-2009
def recent_top_splash_finder(soup, _):
  drudge_top_headlines = soup.find('div', {'id': 'drudgeTopHeadlines'})

  if not drudge_top_headlines:
    raise ParseError("id: 'drudgeTopHeadlines' not found")

  splash = find_splash_with_font_size(drudge_top_headlines)

  top_links = drudge_top_headlines.find_all('a')
  if top_links: 
    top_links = set(top_links)
    top_links = top_links.difference(splash)

  return DrudgePageMetadata(splash_set=splash, top_set=top_links)


def parse_main_and_splash(soup, page_dt):
  # we've got different parsing methods for earlier and later iterations
  # of the drudge report
  metadata_parser = recent_top_splash_finder if page_dt >= NEW_HTML_BEGINS else early_top_splash_finder
  metadata = metadata_parser(soup, page_dt)
  return metadata 

