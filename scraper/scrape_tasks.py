from drudge_scraper import *
import csv
import urlparse
import re

IRRELLEVANT_DOMAINS = {
  'fastclick.net',
  'drudgereportArchives.com',
  'security.google.com',
  'a.tribalfusion.com'
}

URL_REGEX = '(.*)(\.com|\.de?|\.co\.uk|\.net|\.org)'

def extract_source(url):
    url = url.lower()
    netloc = urlparse.urlparse(url).netloc
    groups = re.match(URL_REGEX,  netloc)
    if groups:
        return groups.groups()
    else:
        return netloc

def hundred_urls():
    return_list = list()
    with open('drudge_page.csv', 'r') as f:
        rows = list(csv.reader(f))[1:100]
    urls = [entry[0] for entry in rows]
    return urls
        
if __name__ == "__main__":
    sample = hundred_urls()
    for entry in sample:
        domain = extract_source(entry)
        if not isinstance(domain, tuple):
        #domain = urlparse.urlparse(entry)
            print entry[:50], '\t', domain
