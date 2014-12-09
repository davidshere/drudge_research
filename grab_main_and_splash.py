from bs4 import BeautifulSoup
import requests
from urllib2 import urlopen
import drudge_scraper as scraper

def get_ten_drudge_pages():
    ## pull a list of ten day pages
    all_day_pages = scraper.day_page_list_generator()
    indices = xrange(0, len(all_day_pages), len(all_day_pages)/10)
    day_pages = [all_day_pages[num].url for num in indices]
    day_page_htmls = [requests.get(day).text for day in day_pages]
    print day_page_htmls
    ## next pull a single drudge page from each page, write
    ## each one to a file for further analysis. 

filename = 'sample_drudge_page.htm'
with open(filename, 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

def top_hed_finder(soup):
    top = soup.find(id='drudgeTopHeadlines')
    top = top.find_all('a')
    top = [link.text.encode('utf-8') for link in top]
    splash = ""
    splash = top.pop()
    return (top, splash)

topheds, mainhed = top_hed_finder(soup)

#print "%s\n\n%s" % (topheds, mainhed)

get_ten_drudge_pages()