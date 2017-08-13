#!/usr/local/bin/env python
# -*- coding: latin-1 -*-

''' We have to use funny encoding here because there are some non-ascii 
    characters on the Drudge Report, and some of them we have to specify
    here
'''

from bs4 import BeautifulSoup
import urllib.parse

from utils import DRUDGE_LOGO_LINKS

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com',
  'www.medintop.com'
]



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

def get_early_top(links, found_splash):
  top_links = []

  # find the index of the element found_splash in
  # the list of links
  try:
    splash_index = links.index(found_splash)
  except ValueError:
    for link in links:
      if link.decode() in DRUDGE_LOGO_LINKS:
        splash_index = links.index(link)

  for j in range(splash_index-1, 0, -1):
    parsed_url = urllib.parse.urlparse(links[j].get('href')).netloc.lower()
    if parsed_url in STOP_DOMAINS:
      return top_links
    top_links.append(links[j])

# starting at the beginning to mid 2009
def early_top_splash_finder(soup):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_early_top(links, splash) or []
  return {'top': top, 'splash': splash}

def get_main_and_splash(soup):
  try:
    return recent_top_splash_finder(soup)
  except ParseError:
    return early_top_splash_finder(soup)