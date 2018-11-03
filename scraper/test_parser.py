import datetime
import unittest

from bs4 import BeautifulSoup, Tag

import transform_page_into_drudge_links

def top_splash_to_text(top_and_splash):
  # don't want to test this
  if top_and_splash['splash']:
    top_and_splash['splash'] = {tag.text for tag in top_and_splash['splash'] if isinstance(tag, Tag)}
  if top_and_splash['top']:
    top_and_splash['top'] = {a.text for a in top_and_splash['top'] if isinstance(a, Tag)}
  return top_and_splash

def load_resource(page_number):
  with open('test/resources/test_file_{}.html'.format(page_number), 'r') as f:
    html = f.read()
  return BeautifulSoup(html, 'lxml') 


class ParserTest(unittest.TestCase):



if __name__ == "__main__":
  unittest.main()
