import datetime
import unittest

from bs4 import BeautifulSoup

from html_parser import transform_day_page
from drudge_data_classes import DayPage

TEST_DATE = datetime.date(1970, 1, 1)

class TestTransformDayPage(unittest.TestCase):
  def test_transform_day_page(self):
    with open('test/resources/test_day_page_1.html') as f:
      html = f.read()

    day_page = DayPage(TEST_DATE)
    day_page.html = html

    links = list(transform_day_page.transform_day_page(day_page))
    
    from test.resources.expected_drudge_pages import expected_drudge_pages
    self.assertEqual(links, expected_drudge_pages)

if __name__ == "__main__":
  unittest.main()
