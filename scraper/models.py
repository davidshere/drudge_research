import asyncio
import collections
import datetime
import logging
import multiprocessing
import time

from aiohttp import ClientSession, ClientError
from bs4 import BeautifulSoup
import requests

from parse_main_and_splash import parse_main_and_splash

DAY_PAGE_FMT_URL = "http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag"
MIN_START_DATE = datetime.date(2001, 11, 18)

SEMAPHORE_COUNT = 5
PROCESS_COUNT = multiprocessing.cpu_count()

DrudgeLink = collections.namedtuple("DrudgeLink", [
    'page_dt',
    'url',
    'hed',
    'is_top',
    'is_splash'
])

# Set up logging. This can't be the best way...
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class FetchError(Exception):
    pass

class DrudgePage(object):
    """ Represents one an individual snapshot of the Drudge Report """

    def __init__(self, url, page_dt):
        self.url = url
        self.page_dt = page_dt

    def process_raw_link(self, link, page_main_links):
        url = link.get('href')
        if url:
            # determine if the link is in the top or the splash
            splash = link == page_main_links['splash']
            top = link in page_main_links['top']

            return DrudgeLink(self.page_dt, url, link.text, top, splash)

    def drudge_page_to_links(self):
        ''' scrape takes a url to an individual drudge page, and 
            scrapes every link.  '''
        processed_links = []
        if hasattr(self, 'html') and self._page_has_content(self.html):
            soup = BeautifulSoup(self.html, 'lxml')
            all_links = soup.find_all('a')

            # a basically blank page with a drudge logo will
            # still get past our _page_has_content filter
            #
            # an empty page, as far as I've seen, has 16 total links
            # on the archive. So, as a last resort, we'll make sure
            # we have at least that many links
            if len(all_links) <= 16:
                return []

            main_links = parse_main_and_splash(soup, self.page_dt)
            for link in all_links:
                processed_link = self.process_raw_link(link, main_links) 
                if processed_link:
                    processed_links.append(processed_link)


        logger.info("Done processing %d links for %s", len(processed_links), self.page_dt)
        return processed_links

    def _page_has_content(self, html):
        """ Returns true if a drudge page has actual content. """
        return b'logo9.gif' in html


class DayPage(object):
    """
    Represents the page on drudgereportarchives.com that contains
    timestamped links to the individual Drudge snapshots, like
    this: http://www.drudgereportarchives.com/data/2017/10/02/index.htm?s=flag

    Handles all the behavior of asynchronously fetching the Drudge snapshots
    and scheduling them to be processed.
    """
    def __init__(self, dt):
        self._loop = asyncio.get_event_loop()
        #self._loop.set_debug(True)
        #if dt < MIN_START_DATE or dt < datetime.date.today():
        #    raise Exception("Cannot process date %s, must be between %s and today" % (dt, datetime.date.today()))
        
        self.dt = dt
        self.url = DAY_PAGE_FMT_URL % (dt.year, dt.month, dt.day)
        self._task_queue = multiprocessing.JoinableQueue()
        self._processed_page_queue = multiprocessing.Queue()

    def _prep_queues(self):
        """
        This method instantiates the queues and processes that we'll use
        to handle turning the fetched HTML into lists of links.
        """
        self._consumers = [
            DrudgePageScrapeHandler(self._task_queue, self._processed_page_queue)
            for _ in range(PROCESS_COUNT)
        ]

        for proc in self._consumers:
            proc.start()

    def _processed_page_queue_to_links(self):
        """
        Takes a queue filled with lists of DrudgeLinks and returns
        a single list of links.

        We're waiting until we have popped everything in the queue
        to add the poison pill. That is not how the tutorials do it,
        but it worked. So we're doing it.
        """
        links = []

        for i, page_links in enumerate(iter(self._processed_page_queue.get, 'STOP')):

            if i == self.num_pages - 1:
                self._processed_page_queue.put('STOP')
            
            links.extend(page_links)

        return links

    def _get_day_page(self):
        """ Fetches HTML for a Day Page """
        response = requests.get(self.url)

        logger.info("Fetched Day Page for %s", self.dt.isoformat())
        return BeautifulSoup(response.content, 'lxml')

    def _drudge_page_from_drudge_page_url(self, link):
        """ Transforms a URL into a DrudgePage object """
        url = link.get('href')
        if url:
            url_dt = url.split('/')[-1]
            page_dt = datetime.datetime.strptime(url_dt, '%Y%m%d_%H%M%S.htm')
            return DrudgePage(
                url=url,
                page_dt=page_dt
            )

    def _link_is_drudge_page(self, link):
        return link.get('href').lower().startswith('http://www.drudgereportarchives.com/data/')

    def _prepare_drudge_pages_for_fetching(self, page_limit):
        """
        Transforms a Day Page's HTML into a list of links
        to individual drudge pages. If valid links are found,
        calls self._prep_queues(). Returns a list of DrudgePage objects.
        """
        all_links = self.day_page.find_all('a')
        links_to_drudge_pages = [link for link in all_links if self._link_is_drudge_page(link)]
        drudge_pages = []
        for link in links_to_drudge_pages:
            page = self._drudge_page_from_drudge_page_url(link)
            # there are two links to each Drudge Page
            if page and link.text != '^':
                drudge_pages.append(page)

        if page_limit:
            drudge_pages = drudge_pages[:page_limit]

        self.has_valid_drudge_page_links = False
        if drudge_pages:
            self.has_valid_drudge_page_links = True
            self._prep_queues()

        return drudge_pages

    async def _fetch_drudge_page(self, page, sem, session):
        logger.info("Fetching drudge page at %s", page.url)

        async with sem, session.get(page.url) as response:
            response = await asyncio.gather(response.read())

        page.html = response[0]
        self._task_queue.put(page)

    async def _generate_fetch_tasks(self, page_limit):
        tasks = []
        sem = asyncio.Semaphore(SEMAPHORE_COUNT)

        # Create client session that will ensure we dont open new connection
        # per each request.
        async with ClientSession() as session:
            pages = self._prepare_drudge_pages_for_fetching(page_limit)
            if pages:
                self.num_pages = len(pages)
                for page in pages:
                    task = asyncio.ensure_future(self._fetch_drudge_page(page, sem, session))
                    tasks.append(task)
            return await asyncio.gather(*tasks)

    def process_day(self, page_limit=None):
        """
        Primary public method. Used to fetch one day's worth of links
        from the drudge archive.

        set page_limit if you only want say the first 10 drudge pages
        """
        logger.info("Fetching Day Page for %s, url: %s", self.dt.isoformat(), self.url)
        links = []

        # schedule async fetch tasks
        try:
            self.day_page = self._get_day_page()
            future = asyncio.ensure_future(self._generate_fetch_tasks(page_limit))
            self._loop.run_until_complete(future)

            # Try adding the 

        except ClientError as e:
            logger.error("Failure on %s, url: %s", self.dt.isoformat(), self.url)
            raise FetchError

        # add poison pills so the queue will know when to stop
        if self.has_valid_drudge_page_links:
            for _ in range(PROCESS_COUNT):
                self._task_queue.put(None)

            # block execution until the queues are empty
            self._task_queue.join()

            links = self._processed_page_queue_to_links()

            # turn off processes
            for proc in self._consumers:
                proc.terminate()

        return links

class DrudgePageScrapeHandler(multiprocessing.Process):
    """
    This class does one thing - pops a Drudge Page off
    of a task queue, processes it, and puts the result
    into a result queue.
    """

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            page = self.task_queue.get()
            if page is None:
                # Poison pill means shutdown
                logger.info('{}: Exiting'.format(proc_name))
                self.task_queue.task_done()
                break
            links = page.drudge_page_to_links()

            self.result_queue.put(links)
            self.task_queue.task_done()



if __name__ == "__main__":
    x = time.time()
    start = datetime.datetime.now()
    dt = datetime.date.today() - datetime.timedelta(days=30)
    dt = datetime.datetime(2002, 9, 21)

    dp = DayPage(dt)
    d = dp.process_day()
    print("day took", time.time() - x)
    print("processed %d pages" % len(set(a.page_dt for a in d)))
