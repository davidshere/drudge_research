import datetime

from bs4 import BeautifulSoup, Tag
import urllib.parse

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com'
]

LOGO_FILENAME = 'logo9.gif'

NEW_HTML_BEGINS = datetime.datetime(2009, 10, 6, 5, 57, 42)


class ParseError(Exception):
  pass


# going back to mid-2009
def recent_top_splash_finder(soup):
  top = soup.find('div', {'id': 'drudgeTopHeadlines'})
  if not top:
    raise ParseError("id: 'drudgeTopHeadlines' not found")
  top = top.find_all('a')
  splash = top.pop()
  return {'top': top, 'splash': splash}


# before mid-2009
def find_splash_with_font_size(soup):
  """ Takes soup and returns the <a> element representing
      the page splash.

      If no link element is found, returns None
  """
  font_size_element = soup.find('font', {"size":"+7"})
  if not font_size_element:
    return None

  # if the HTML is malformed, this will return None
  link = font_size_element.find('a')
  if link:
    return link

  # returns -1 if it finds nothing
  link = font_size_element.next.find('a')
  if link != -1:
    return link


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


def get_early_top(links, found_splash):
  top_links = []

  # find the index of the element found_splash in
  # the list of links
  if found_splash:
    splash_index = links.index(found_splash)
  else:
    for link in links:
      if is_logo_link(link):
        splash_index = links.index(link)
        break

  for j in range(splash_index-1, 0, -1):
    parsed_url = urllib.parse.urlparse(links[j].get('href')).netloc.lower()
    if parsed_url in STOP_DOMAINS:
      return top_links

    if links[j].text:
      top_links.append(links[j])


# starting at the beginning to mid 2009
def early_top_splash_finder(soup):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_early_top(links, splash) or []
  return {'top': top, 'splash': splash}


def parse_main_and_splash(soup, page_dt):
  if page_dt >= NEW_HTML_BEGINS:
    return recent_top_splash_finder(soup)
  else:
    return early_top_splash_finder(soup)
