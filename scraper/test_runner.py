import datetime
import unittest

from archive_to_s3 import *
from models import DayPage

class ScrapeTests(unittest.TestCase):

	def setUp(self):
		self.runner = ScraperRunner()

	def test_filename_transform(self):
		expected_result = (['H1Y2017'] * 6) + (['H2Y2017'] * 6)

		sample_input = [datetime.datetime(2017, month, 1) for month in range(1, 13)]
		filenames = [self.runner._dt_to_year_half_str(dt) for dt in sample_input]
		
		self.assertEqual(filenames, expected_result)

	def test_scrape_writing_logic(self):
		self.runner.end_date = datetime.datetime(2017, 10, 1)
	
		# do we know how to change from one file to the next?
		self.runner.current_file = 'H1Y2017'
		sample_date = datetime.datetime(2017, 6, 30)
		page = DayPage(sample_date)
		self.assertTrue(self.runner._should_scraped_pages_should_be_written_to_disk(page))

		# do we know to continue when it's not the end?
		self.runner.current_file = 'H2Y2017'
		sample_date = datetime.datetime(2017, 9, 15)
		page = DayPage(sample_date)
		self.assertFalse(self.runner._should_scraped_pages_should_be_written_to_disk(page))

		# do we know to stop at the end?
		sample_date = datetime.datetime(2017, 9, 30)
		page = DayPage(sample_date)
		self.assertTrue(self.runner._should_scraped_pages_should_be_written_to_disk(page))


		self.runner.current_file = 'H2Y2016'
		self.runner.end_date = datetime.datetime(2017, 1, 3)
		sample_date = datetime.datetime(2016, 12, 30)
		page = DayPage(sample_date)
		self.assertFalse(self.runner._should_scraped_pages_should_be_written_to_disk(page))

		self.runner.current_file = 'H2Y2016'
		self.runner.end_date = datetime.datetime(2017, 1, 3)
		sample_date = datetime.datetime(2016, 12, 31)
		page = DayPage(sample_date)
		self.assertTrue(self.runner._should_scraped_pages_should_be_written_to_disk(page))


if __name__ == "__main__":
	unittest.main()