import asyncio
import collections
import datetime

from aiohttp import ClientSession
from bs4 import BeautifulSoup
import requests

from grab_main_and_splash import get_main_and_splash

DAY_PAGE_FMT_URL = "http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag"
DRUDGE_PAGE_URL_PREFIX = 'http://www.drudgereportArchives.com/data/'

DRUDGE_LINK_FIELD_NAMES = ['page_dt', 'url', 'hed', 'is_top', 'is_splash']
DrudgeLink = collections.namedtuple("DrudgeLink", DRUDGE_LINK_FIELD_NAMES)

SEMAPHORE_COUNT = 3

BYTES_TRUE = bytes(str(True), 'utf-8')
BYTES_FALSE = bytes(str(False), 'utf-8')

class DayPage(object):

    def __init__(self, dt):
        self.loop = asyncio.get_event_loop()
        self.url = DAY_PAGE_FMT_URL % (dt.year, dt.month, dt.day)

    def get_day_page(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.content, 'lxml')

    def drudge_page_from_drudge_page_url(self, link):
        url = link['href']
        url_dt = url.split('/')[-1]
        page_dt = datetime.datetime.strptime(url_dt, '%Y%m%d_%H%M%S.htm')
        return DrudgePage(
            url=url,
            page_dt=page_dt
        )

    def drudge_pages(self):
        all_links = self.day_page.find_all('a')
        links = []
        for link in all_links:
            try:
                page = self.drudge_page_from_drudge_page_url(link)
                links.append(page)
            except ValueError:
                pass

        return links

    async def bound_fetch_drudge_page(self, page, sem, session):
        async with sem:
            page.html = await self.fetch_drudge_page(page.url, session)
            return page

    async def fetch_drudge_page(self, url, session):
        async with session.get(url) as response:
            return await response.read()


    async def get_drudge_pages(self):
        tasks = []

        # Create client session that will ensure we dont open new connection
        # per each request.

        sem = asyncio.Semaphore(SEMAPHORE_COUNT)

        async with ClientSession() as session:
            pages = self.drudge_pages()
            for page in pages:
                task = asyncio.ensure_future(self.bound_fetch_drudge_page(page, sem, session))
                tasks.append(task)

            return await asyncio.gather(*tasks)

    def scrape(self):
        self.day_page = self.get_day_page()
        future = asyncio.ensure_future(self.get_drudge_pages())
        return self.loop.run_until_complete(future)

class DrudgePage(object):

    def __init__(self, url, page_dt):
        self.url = url
        self.page_dt = page_dt.isoformat().encode()

    def process_raw_link(self, link, page_main_links):
        """ We're sending this up to S3 and it's all gotta
            be bytes.
        """
        splash = BYTES_FALSE
        top = BYTES_FALSE

        url = link['href'].encode()
        text = link.text.encode()

        if link.text == page_main_links['splash']:
            splash = BYTES_TRUE
        if link.text in page_main_links['top']:
            top = BYTES_TRUE
        return DrudgeLink(self.page_dt, url, text, top, splash)

    def get_links(self):
        ''' scrape takes a url to an individual drudge page, and 
            scrapes every link.  '''
        soup = BeautifulSoup(self.html, 'lxml')
        raw_links = soup.find_all('a')
        if self._page_has_content(soup):
            main_links = get_main_and_splash(soup)
            return [self.process_raw_link(link, main_links) for link in raw_links]

    def _page_has_content(self, soup):
        """ Returns true if a drudge page has actual content. """
        return 'logo9.gif' in str(soup)


if __name__ == "__main__":
    start = datetime.datetime.now()
    dt = datetime.date.today() - datetime.timedelta(days=1)
    dp = DayPage(dt)
    d = dp.scrape()
    links = []
    for link in d:
        for item in link.get_links():
            links.append(item)
