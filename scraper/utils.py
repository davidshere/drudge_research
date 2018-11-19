import datetime

from bs4 import BeautifulSoup

def day_page_url_from_dt(dt: datetime.date) -> str:
  fmt_url = 'http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag'
  return fmt_url % (dt.year, dt.month, dt.day)

def remove_dra_tags_from_soup(soup: BeautifulSoup):
  """ 
  For each <td> with a class "text9" (indicating the section was added
  by the archive), mutate the parent soup object to remove the <td>.

  Ditto for tags with the attribute target="_top"
  """
  dra_tds = soup.find_all('td', {'class': 'text9'})
  for td in dra_tds:
    td.decompose()

  top_targets = soup.find_all(target='_top')
  for target in top_targets:
    target.decompose()



