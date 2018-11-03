import collections
import datetime

from bs4 import BeautifulSoup, Tag
import urllib.parse

from drudge_data_classes import DrudgeLink

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
    return set()

  splash_links = font_size_element.find_all('a')
  if splash_links:
    return set(splash_links)

  # if the HTML is malformed or the headline isn't a link,
  # this line will return -1
  link = font_size_element.next.find('a')
  if link != -1:
    return set([link])


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
  found_splash = found_splash or set()
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
      return top_links

    if link.text and link not in found_splash:
      top_links.add(link)
  raise ParseError("get_early_top returned None - it shouldn't do that")


def early_top_splash_finder(soup, page_dt):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_early_top(links, splash, page_dt)
  return {
    'top': top,
    'splash': splash or set()
  }


# going back to mid-2009
def recent_top_splash_finder(soup):
  drudge_top_headlines = soup.find('div', {'id': 'drudgeTopHeadlines'})

  if not drudge_top_headlines:
    raise ParseError("id: 'drudgeTopHeadlines' not found")

  splash = find_splash_with_font_size(drudge_top_headlines)

  top_links = drudge_top_headlines.find_all('a') or []
  top_links = set(top_links)
  top_links = top_links.difference(splash)

  return {'top': top_links, 'splash': splash}


def process_raw_link(link, page_main_links, page_dt):
  url = link.get('href')
  if url:
    # determine if the link is in the top or the splash
    splash = link == page_main_links['splash']
    top = link in page_main_links['top']

    return DrudgeLink(url, page_dt, link.text, top, splash)

def parse_main_and_splash(soup, page_dt):
  # we've got different parsing methods for earlier and later iterations
  # of the drudge report
  if page_dt >= NEW_HTML_BEGINS:
    return recent_top_splash_finder(soup)
  else:
    return early_top_splash_finder(soup, page_dt)

def transform_page_into_drudge_links(soup, page_dt):
  """ Main transformation method. """
  all_links = soup.find_all('a')

  # if there are fewer than 16 links on the page
  # it was likely an error of some kind
  if len(all_links) <= 16:
    return []
    raise ParseError("Not enough links on archive page for {}".format(page_dt))

  metadata = parse_main_and_splash(soup, page_dt)

  # We need to loop through the links and create DrudgeLink objects.
  processed_links = []
  for link in all_links:

    drudge_link = process_raw_link(link, metadata, page_dt)

    if drudge_link:
      processed_links.append(drudge_link)

  return processed_links
