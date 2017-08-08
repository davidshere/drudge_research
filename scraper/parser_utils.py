'''
Test:
24 - modern
11 - older
9 - no link for the splash
'''
import urlparse

STOP_DOMAINS = [
  'harvest.adgardener.com',
  'a.tribalfusion.com'
]

class ParseError(Exception):
	pass

# going back to mid 2009
def recent_top_splash_finder(soup):
	# This works for all known iterations of the drudge report in the last six years
	top = soup.find('div', {'id': 'drudgeTopHeadlines'})
	if not top:
		raise ParseError(msg="id: 'drudgeTopHeadlines' not found")
	top = top.find_all('a')
	top = [link.text.encode('utf-8') for link in top]
	splash = top.pop()
	return {'top': top, 'splash': splash}

# starting in mid 2007 to mid 2009
def get_splash(soup):
  tables = soup.findAll('table')[1]
  centers = tables.findAll('center')
  return centers[2].findAll('a')[0]

def get_top(links, found_splash):
  top_links = []
  splash_index = links.index(found_splash)
  for j in range(splash_index-1, 0, -1):
    parsed_url = urlparse.urlparse(links[j].get('href')).netloc.lower()
    if parsed_url in STOP_DOMAINS:
      return top_links
    top_links.append(links[j])

def get_top_and_splash_recent(soup):
  """ parses top and splash out of 2009-present pages """
  all_links = soup.findAll('a')
  splash = get_splash(soup)
  top = get_top(all_links, splash)  
  return {'top': top, 'splash': splash}