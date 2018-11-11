import datetime
import unittest

from bs4 import BeautifulSoup, Tag

from parser.parser import transform_page_into_drudge_links

def load_resource(page_number):
  with open('test/resources/test_file_{}.html'.format(page_number), 'r') as f:
    html = f.read()
  return BeautifulSoup(html, 'lxml') 


class ParserTest(unittest.TestCase):
  pass


if __name__ == "__main__":
  unittest.main()
