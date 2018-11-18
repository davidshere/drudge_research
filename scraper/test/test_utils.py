import datetime
import unittest

import utils


class TestUtils(unittest.TestCase):
  def test_day_page_url(self):
    test_date = datetime.datetime(1970, 1, 1, 0, 0).date()
    expected_url = "http://www.drudgereportarchives.com/data/1970/01/01/index.htm?s=flag"
    actual_url = utils.day_page_url_from_dt(test_date)
    self.assertEqual(expected_url, actual_url) 
    
