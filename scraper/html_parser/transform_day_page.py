import datetime

from bs4 import BeautifulSoup

from drudge_data_classes import DayPage, DrudgePage
import utils

def transform_day_page(page: DayPage) -> list:
  """ 
  Take html of a day page and transform it into a list of DrudgePage
  objects.
  """
  # we use lxml because this page is usually well formed
  soup = BeautifulSoup(page.html, 'lxml')
  
  # generate all <a> tags that aren't part of common archive html
  utils.remove_dra_tags_from_soup(soup)
  all_links = soup.find_all('a', {'target': ''})
  for link in all_links:
    href = link.get("href").lower()
    
    # make sure there is an href and the right kind of archive link, and
    # yield a drudge page
    if href and href.startswith('http://www.drudgereportarchives.com/data/'):
      url_dt = href.split('/')[-1]
      page_dt = datetime.datetime.strptime(url_dt, '%Y%m%d_%H%M%S.htm')
      yield DrudgePage(href, page_dt)

