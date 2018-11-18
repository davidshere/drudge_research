import datetime
import unittest

from drudge_data_classes import DayPage

class TestDataClasses(unittest.TestCase):
  def test_day_page_constructor(self):
    test_date = datetime.datetime(1970, 1, 1, 0, 0).date()
    day_page = DayPage(test_date)

    self.assertEqual(day_page.dt, test_date)
    self.assertEqual(day_page.url, "http://www.drudgereportarchives.com/data/1970/01/01/index.htm?s=flag")
