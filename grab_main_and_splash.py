from bs4 import BeautifulSoup
from urllib2 import urlopen

'''
url = 'http://www.drudgereportarchives.com/data/2014/02/03/20140203_000653.htm'

html = urlopen(url).read()
'''

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
    main = set(top)
    return (main, splash)

topheds, mainhed = top_hed_finder(soup)

print topheds
print
print mainhed
