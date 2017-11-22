import datetime
import unittest

from models import *

from test.resources.drudge_page_test import test_bad_html_expected_results

class DrudgePageTest(unittest.TestCase):

	def test_bad_html(self):
		sample_dt = datetime.datetime(2007, 7, 30)
		sample_url = 'http://www.drudgereportarchives.com/data/2007/07/30/20070730_190020.htm'
		page = DrudgePage(sample_url, sample_dt)

		with open('test/resources/drudge_page_test/parser_test_20170730190020.html', 'rb') as f:
			page.html = f.read()

		actual_results = page.drudge_page_to_links()
		expected_results = test_bad_html_expected_results.expected_results

		self.assertEqual(actual_results, expected_results)



if __name__ == "__main__":
	unittest.main()