##!/usr/local/bin/env python
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

#START_LINK = 
STOP_LINK = u'<a href="http://www.drudgereport.com/"><img border="0" height="85" src="http://www.drudgereport.com/logo9.gif" width="610"/></a>'

def top_splash_finder(soup):
  first_try = recent_top_splash_finder(soup)
  if first_try:
    return first_try
  else:

    return {'top': top, 'splash': splash}


def get_drudge_pages():
    ''' Fetches html for some number of day pages and returns a list of
        drudge page objects from the first link in each day page '''
    list_of_drudge_pages = []
    all_day_pages = scraper.day_page_list_generator()
    indices = xrange(0, len(all_day_pages), 200)
    day_pages = [all_day_pages[i] for i in indices]
    for day in day_pages:
      print day.drudge_date
      first_drudge_page = day.scrape_day_page()[0]
      list_of_drudge_pages.append({day.drudge_date: first_drudge_page})
    return list_of_drudge_pages

def drudge_page_file_writer():
    all_day_pages = scraper.day_page_list_generator()
    indices = xrange(0, len(all_day_pages), 200)
    day_pages = [all_day_pages[i] for i in indices]
    print day_pages[0]
    print len(day_pages)

## test code ##
def load_html(page_number):
  with open('splash_research/test_files/test_file_%d.html' % page_number, 'r') as f:
    html = f.read()
  return BeautifulSoup(html, 'lxml') 

def single_page_tester(page_number):
  soup = load_html(page_number)
  main = top_splash_finder(soup)
  return '=====\ntop:\n%s\n\nsplash:\n%s' % (main['top'], main['splash'])

def find_splash_with_font_size(soup):
  font_size_element = soup.find('font', {"size":"+7"})
  link = font_size_element.find('a')
  if link:
    return link
  return font_size_element.next.find('a')


# starting in mid 2004 to mid 2009
def get_2004_to_2009(soup):
  splash = find_splash_with_font_size(soup)
  links = soup.find_all('a')
  top = get_top(links, splash)
  return {'top': top, 'splash': splash}

def get_top(links, found_splash):
  print found_splash
  top_links = []
  try:
    splash_index = links.index(found_splash)
  except ValueError:
    for link in links[8:]:
      if link.decode() == STOP_LINK:
        splash_index = links.index(link)
  for j in range(splash_index-1, 0, -1):
    parsed_url = urlparse.urlparse(links[j].get('href')).netloc.lower()
    if parsed_url in STOP_DOMAINS:
      return top_links
    top_links.append(links[j])

if __name__ == '__main__':
  # can't get 9 or earlier to work for now
  # issue is, we we're relying on finding a link for the splash
  # to work backwards towards the top headlines
  # that doesn't necessarily work if the splash is text

  # alternative strategy could be to find the first link, work back
  # from there
  for i in range(24, 0, -1):
    print i,
    soup = load_html(i)
    try:
      print recent_top_splash_finder(soup)
    except ParseError:
      print get_2004_to_2009(soup)




    """
    print i
    soup = load_html(i)
    all_links = soup.findAll('a')
    splash = get_splash(soup)
    if splash:
      top = get_top(all_links, splash)
      print splash
      print len(top)
      print top
      print '\n\n**\n'
    else:
      print '?'

    break
    """


