#!/usr/local/bin/env python
# -*- coding: latin-1 -*-

''' We have to use funny encoding here because there are some non-ascii 
    characters on the Drudge Report, and some of them we have to specify
    here
'''

from bs4 import BeautifulSoup
import urlparse

from parser_utils import recent_top_splash_finder
from parser_utils import ParseError

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com'
]

STOP_LINKS = (
  u'<a href="http://www.drudgereport.com/"><img border="0" height="85" src="http://www.drudgereport.com/logo9.gif" width="610"/></a>',
  u'<a href="http://www.drudgereport.com"><img border="0" height="85" src="http://www.drudgereport.com/logo9.gif" width="610"/></a>'
)

class ParseError(Exception):
  pass

# this works on pages going back to mid 2009
def recent_top_splash_finder(soup):
  # This works for all known iterations of the drudge report in the last six years
  top = soup.find('div', {'id': 'drudgeTopHeadlines'})
  if not top:
    raise ParseError("id: 'drudgeTopHeadlines' not found")
  top = top.find_all('a')
  splash = top.pop()
  return {'top': top, 'splash': splash}



def find_splash_with_font_size(soup):
  """ Takes soup and returns the <a> element representing
      the page splash.

      If no link element is found, returns None
  """
  font_size_element = soup.find('font', {"size":"+7"})

  # if the HTML is malformed, this will return None
  link = font_size_element.find('a')
  if link:
    return link

  # returns -1 if it finds nothing
  link = font_size_element.next.find('a')
  if link != -1:
    return link

def get_early_top(links, found_splash):
  top_links = []

  # find the index of the element found_splash in
  # the list of links
  try:
    splash_index = links.index(found_splash)
  except ValueError:
    for link in links:
      if link.decode() in STOP_LINKS:

        splash_index = links.index(link)

  for j in range(splash_index-1, 0, -1):
    parsed_url = urlparse.urlparse(links[j].get('href')).netloc.lower()
    if parsed_url in STOP_DOMAINS:
      return top_links
    top_links.append(links[j])

# starting at the beginning to mid 2009
def early_top_splash_finder(soup):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_early_top(links, splash)
  return {'top': top, 'splash': splash}

def get_main_and_splash(soup):
  try:
    return recent_top_splash_finder(soup)
  except ParseError:
    return early_top_splash_finder(soup)