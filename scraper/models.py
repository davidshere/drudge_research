import asyncio
import collections
import datetime
import logging

from aiohttp import ClientSession
from bs4 import BeautifulSoup
import requests
import retrying

from grab_main_and_splash import get_main_and_splash

DAY_PAGE_FMT_URL = "http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag"
DRUDGE_PAGE_URL_PREFIX = 'http://www.drudgereportArchives.com/data/'

DRUDGE_LINK_FIELD_NAMES = ['page_dt', 'url', 'hed', 'is_top', 'is_splash']
DrudgeLink = collections.namedtuple("DrudgeLink", DRUDGE_LINK_FIELD_NAMES)

SEMAPHORE_COUNT = 5

class FetchError(Exception):
    pass

class DayPage(object):

    def __init__(self, dt):
        self.loop = asyncio.get_event_loop()
        self.url = DAY_PAGE_FMT_URL % (dt.year, dt.month, dt.day)

    def get_day_page(self):
        response = requests.get(self.url)

        logging.info("Fetched Day Page for %s", self.dt.isotime())
        return BeautifulSoup(response.content, 'lxml')

    def drudge_page_from_drudge_page_url(self, link):
        url = link.get('href')
        if url:
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
                if page:
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


    async def fetch_drudge_pages(self):
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

    @retrying.retry(retry_on_exception=lambda exception: isinstance(exception, FetchError))
    def scrape(self):
        try:
            logging.info("Fetching Day Page for %s, url: %s", (self.dt.isotime(), self.url))
            self.day_page = self.get_day_page()
            future = asyncio.ensure_future(self.fetch_drudge_pages())
            drudge_pages = self.loop.run_until_complete(future)
        except:
            raise FetchError

        links = []
        for page in drudge_pages:
            links.extend(page.scrape_drudge_page())
        return links

class DrudgePage(object):

    def __init__(self, url, page_dt):
        self.url = url
        self.page_dt = page_dt

    def process_raw_link(self, link, page_main_links):
        url = link.get('href')
        if url:
            text = link.text

            splash = link.text == page_main_links['splash']
            top = link.text in page_main_links['top']

            return DrudgeLink(self.page_dt, url, text, top, splash)

    def scrape_drudge_page(self):
        ''' scrape takes a url to an individual drudge page, and 
            scrapes every link.  '''
        soup = BeautifulSoup(self.html, 'lxml')

        processed_links = []
        if self._page_has_content(soup):

            main_links = get_main_and_splash(soup)
            
            for link in soup.find_all('a'):
                processed_link = self.process_raw_link(link, main_links) 
                if processed_link:
                    processed_links.append(processed_link)

        return processed_links

    def _page_has_content(self, soup):
        """ Returns true if a drudge page has actual content. """
        return 'logo9.gif' in str(soup)


if __name__ == "__main__":
    start = datetime.datetime.now()
    dt = datetime.date.today() - datetime.timedelta(days=30)
    dp = DayPage(dt)
    d = dp.scrape()
    print(d[0])
