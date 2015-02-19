#!/usr/bin/env python
# -*- coding: latin-1 -*-

from bs4 import BeautifulSoup
import requests
import re
import drudge_scraper as scraper

CURRENT_FILENAME = 'splash_research/current_drudge.html'
with open(CURRENT_FILENAME, 'r') as f:
  html = f.read()
  csoup = BeautifulSoup(html, 'lxml')

SAMPLE_FILENAME = 'splash_research/sample_drudge_page.htm'
with open(SAMPLE_FILENAME, 'r') as f:
  html = f.read()
  ssoup = BeautifulSoup(html, 'lxml')

OLDER_FILENAME = 'splash_research/older_drudge_page.html'
with open(OLDER_FILENAME, 'r') as f:
  html = f.read()
  osoup = BeautifulSoup(html, 'lxml')


class MainAndSplashFinder(object):

  date_dict = {}

  def __init__(self):
    pass

  def which_splash_finder(self):
    '''
    return date_dict[drudge_date]
    '''
    pass

  def main_and_splash(self):
    return 



def new_old_hed_finder(soup):
 #finding the splash and top headlines       
  top = soup.find('div', {'id': 'drudgeTopHeadlines'}).find_all('a')
  top = [link.text.encode('utf-8') for link in top]
  splash_text = top.pop()
  main_text = list(top)
  print "%s\n\n%s" % (main_text, splash_text)

def hed_and_splash_finder(soup):
  # if time/date > Oct 6, 2009 05:57:42 EXT (10:57:42 GMT)
  try:
    top = soup.find('div', {'id': 'drudgeTopHeadlines'})
    top = top.find_all('a')
    top = [link.text.encode('utf-8') for link in top]
    splash = top.pop()
    return (top, splash)
  except:
    return (None, None)



def hed_finder_1(soup):
  '''Applies to archives from the beginning of the archive until...

    Maybe October 2002?
  '''
  archive_url_part = 'drudgereportarchives.com'
  main_links_come_after = [
    'DrudgeReportArchives.com',
    'Today\'s DrudgeReport.com',
    'Drudge´s Special Reports',
    'DrudgeReport.com',
    'Drudge\'s Special Reports',
    'Drudge on Twitter',
    'Recent Headlines',
    'Pictures',
    '',
    '',
    ' ',
    'Popular Headlines',
    'Time Line'
  ]
  all_links = soup.find_all('a')
  top = list()
  for link in all_links:
    if top and link.text == '': # because a link w/o text comes after the splash
      break

    if link.has_attr('href') and link.text not in main_links_come_after:
      if not re.search(archive_url_part, link.get('href')):
        top.append(link)

  if top:
    splash = top.pop()
  return {top, splash


def get_drudge_pages():
    ''' Fetches html for some number of day pages and returns a list of
        drudge page objects from the first link in each day page '''
    list_of_drudge_pages = []
    all_day_pages = scraper.day_page_list_generator()
    indices = xrange(0, len(all_day_pages), 200)
    day_pages = [all_day_pages[num] for num in indices]
    for day in day_pages:
      print day.drudge_date
      first_drudge_page = day.scrape_day_page()[0]
      list_of_drudge_pages.append({day.drudge_date: first_drudge_page})
    return list_of_drudge_pages

def drudge_page_file_writer():
    all_day_pages = scraper.day_page_list_generator()
    indices = xrange(0, len(all_day_pages), 200)
    day_pages = [all_day_pages[num] for num in indices]
    print day_pages[0]
    print len(day_pages)

if __name__ == '__main__':
  drudge_page_objects = get_drudge_pages() # fetching list of drudge objects
  drudge_page_soups = []
  for number, page in enumerate(drudge_page_objects): # creating list of soup objects
    url = page.url
    html = requests.get(url).text
    with open('scraper_research/test_file_%d.html' % number, 'w') as f:
      f.write(html.encode('utf-8'))
    soup = BeautifulSoup(html)
    drudge_page_soups.append(soup)


  old_heds = map(lambda page: hed_finder_1(page), drudge_page_soups)
  for hed in old_heds:
    print hed[0]
    print hed[1]

