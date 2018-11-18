import datetime
import unittest
import sys
sys.path.append('..')

from bs4 import BeautifulSoup, Tag

from drudge_data_classes import DrudgePageMetadata, DrudgeLink
import html_parser.parser as parser

TEST_LINK_TEXT = "OUTRAGE!"
TEST_LINK = '<a href="http://example.com">{}</a>'.format(TEST_LINK_TEXT)
TEST_DATETIME = datetime.datetime(1970, 1, 1, 0, 0)

def load_text(page_identifier):
  with open('test/resources/{}.html'.format(page_identifier), 'r') as f:
    return f.read()


class ParserTest(unittest.TestCase):
  @unittest.skip("getting rid of this method hopefully")
  def tets_is_archive_link(self):
    top_true = BeautifulSoup('<a href="example.com" target="_top">text</a>', 'html5lib')
    text9_true = BeautifulSoup('<a href="example.com" class="text9">text</a>', 'html5lib') 
  
    top_false = TEST_LINK
    text9_false = TEST_LINK

    self.assertEqual(parser.is_archive_link(top_true), True)
    self.assertEqual(parser.is_archive_link(text9_true), True)
    self.assertEqual(parser.is_archive_link(top_false), False)
    self.assertEqual(parser.is_archive_link(text9_false), False)

  ##
  ## testing process_raw_link
  ## 
  def test_process_link_not_in_metadata(self):
    link = BeautifulSoup(TEST_LINK, "lxml").find('a') 
    meta = DrudgePageMetadata()
    processed_drudge_link = parser.process_raw_link(link, meta, TEST_DATETIME)
    expected_drudge_link = DrudgeLink("http://example.com", TEST_DATETIME, link.text, False, False)
    self.assertEqual(processed_drudge_link, expected_drudge_link)

  def test_process_splash_link(self):
    link = BeautifulSoup(TEST_LINK, "lxml").find('a') 
    meta = DrudgePageMetadata(splash_set=set([TEST_LINK_TEXT]))
    processed_drudge_link = parser.process_raw_link(link, meta, TEST_DATETIME)
    expected_drudge_link = DrudgeLink("http://example.com", TEST_DATETIME, link.text, False, True)
    self.assertEqual(processed_drudge_link, expected_drudge_link)

  def test_process_top_link(self):
    link = BeautifulSoup(TEST_LINK, "lxml").find('a') 
    meta = DrudgePageMetadata(top_set=set([TEST_LINK_TEXT]))
    processed_drudge_link = parser.process_raw_link(link, meta, TEST_DATETIME)
    expected_drudge_link = DrudgeLink("http://example.com", TEST_DATETIME, link.text, True, False)
    self.assertEqual(processed_drudge_link, expected_drudge_link)

  ##
  ## testing html_into_drudge_links
  ##
  def test_html_into_drudge_links(self):
    resource_id = "20060406_000558"
    html = load_text(resource_id)
    links = parser.html_into_drudge_links(html, TEST_DATETIME)

    from test.resources.expected_drudge_links_20060406_000558 import expected_drudge_links
    self.assertEqual(links, expected_drudge_links)



if __name__ == "__main__":
  unittest.main()
