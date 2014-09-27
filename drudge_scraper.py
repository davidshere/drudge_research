from bs4 import BeautifulSoup

import csv
from datetime import date
import re
import socket
from sys import argv
from time import gmtime
from urllib2 import urlopen

TEMP_DAYS_FILENAME = 'day.csv'

class DayPage(object):

    socket.setdefaulttimeout(5)
    
    def __init__(self, day_page_url, drudge_date, day_order):
        self.url = day_page_url
        self.drudge_date = drudge_date
        self.day_order = day_order
        
    def try_request(self, url):
        success = False
        attempt_count = 0
        while not success:
            try:
                html = urlopen(self.url).read()
                success = True
                return html
            except:
                attempt_count +=1
                print "attempt", attempt_count, "failed" 

    def day_page_scraper(self):
        '''Goes through a day page and scrapes the links to the 
        individual drudge pages'''
        html = self.try_request(self.url)
        url_front = 'http://www.drudgereportArchives.com/data/'
        soup = BeautifulSoup(html, 'lxml')
        all_urls = soup.find_all('a')
        ## add a BS functtion that gets all of the link text
        drudge_url_list = [{'url':url['href'], 
                            'time':url.text.encode('utf-8').strip(), 
                            'drudge_date':self.drudge_date,
                            'day_order':self.day_order} 
                            for url in all_urls if 
                                url['href'][0:41] == url_front]
                                
        drudge_url_list = [entry for entry in drudge_url_list if entry['time']!="^"]
        return [DrudgePage(self, 
                           drudge_page_data['url'], 
                           drudge_page_data['time'])
                           for drudge_page_data in drudge_url_list]
        
class DrudgePage(object):

    socket.setdefaulttimeout(5)
    
    def __init__(self, day_page_obj, url, time): 
        self.url = url
        self.time = time
        self.drudge_links = []
        self.link_count = None
        
    def try_request(self, url):
        success = False
        attempt_count = 0
        while not success:
            try:
                html = urlopen(self.url).read()
                success = True
                return html
            except:
                attempt_count +=1
                print "attempt", attempt_count, "failed"             
        
    def drudge_page_scraper(self):
        ''' drudge_page_scraper takes a url to an individual drudge page, and 
            scrapes every link.  '''               
        html = self.try_request(self.url)
        soup = BeautifulSoup(html, 'lxml')
        try:
            #finding the splash and top headlines       
            top = soup.find(id='drudgeTopHeadlines')
            top = top.find_all('a')
            top = [link.text.encode('utf-8') for link in top]
            splash_text = ""
            splash_text = top.pop()
            main_text = set(top)
        except:
            splash_text = ""
            main_text = ""
        
        return_list = []
        all_urls = soup.find_all('a')
        
        # building the linkid front, initializing the link counter
        monthstr = str(self.drudge_date.month)
        daystr = str(self.drudge_date.day)
        yearstr = str(self.drudge_date.year)[2:]
        if len(monthstr) == 1:
            monthstr = "0" + monthstr
        if len(daystr) == 1:
            daystr = "0" + daystr
        datestr = yearstr + monthstr + daystr
        timestr = "".join(self.time.split(":"))
        id_front = datestr+timestr
        link_counter = 1
                
        for link in all_urls:           
            splash = False
            main = False
            if link.text == splash_text:
                splash = True
            if link.text in main_text:
                main = True
            # creating the linkid
            if link_counter < 10:
                countstr = "00" + str(link_counter)
            elif link_counter < 100 and link_counter >= 10:
                countstr = "0" + str(link_counter)
            else:
                countstr = str(link_counter)
            linkid = id_front + countstr
            link_counter+=1
            print linkid
            if splash or main:
                drudge_link_obj = DrudgeLink(linkid, link['href'], 
                                             link.text.encode('utf-8').lower(), 
                                             self,
                                             main,
                                             splash)
            else:
                drudge_link_obj = DrudgeLink(linkid, link['href'], 
                                             link.text.encode('utf-8').lower(), 
                                             self, 
                                             main, 
                                             splash) 
            return_list.append(drudge_link_obj)
        self.drudge_links = return_list
        return return_list
    
class DrudgeLink(object):
    def __init__(self, linkid, url, hed, drudge_page_object, main=False, splash = False, ):
        self.url = url
        self.hed = hed
        self.main = main
        self.splash = splash
        self.source = None
        self.linkid = linkid
        
    def extract_source(self):
        domain = re.search(r'\/[a-zA-Z0-9.]+', self.url).group()[1:]
        domain_components = domain.split(".")
        if len(domain_components) == 2:
            self.source = domain_componenets[0]
        else:
            self.source = domain_componenets[1]
        
    def list_dump(self):
        #print self.linkid
        return [self.linkid,
                self.url, 
                self.hed, 
                self.main, 
                self.splash, 
                self.drudge_date.year, 
                self.drudge_date.month, 
                self.drudge_date.day, 
                self.day_order, 
                self.time]

def day_page_url_generator(year, month, day):
    ''' Given a year, month, and a day, assembles a URL for the drudge
    archive page that day and passes it to a Url object, which it retutns '''
    base_url = "http://www.drudgereportarchives.com/data/"
    url_end = "/index.htm?s=flag"        
    if month < 10:
        month = "0" + str(month)
    if day < 10:
        day = "0" + str(day)
    date_portion = str(year) + "/" + str(month) + "/" + str(day)
    url_components = [base_url, date_portion, url_end]
    day_page_url = "".join(url_components)
    return day_page_url

def dump_day_pages_to_file(list_of_day_pages, filename):
    with open(filename, 'w') as f:
        writer = csv.writer(f)      
        for day in list_of_day_pages:
            writer.writerow([day.day_order,
                             day.drudge_date,
                             day.url])

def day_page_list_generator(start = {}, end = {}):
    '''Returns a list of urls to for each day page in the drudge Archive 
    either between the beginning of the archive until today or from
    a specified start date to a specified end date. The date take the for of a
    dictionary, like this:
    
                {'year': year, 'month': month, 'day': day}
    
    '''
    
    # initializing variables, years, months, and days
    year_list = range(2001, gmtime()[0]+1)
    day_order = -321 # because the function makes urls for 321 days before the
                     # first day page in the drudge archive                    
    month_days = [(1,31), (2, 28), (3, 31), (4, 30), (5, 31), (6, 30), (7, 31),
                 (8, 31), (9, 30), (10, 31), (11, 30), (12, 31)]
    full_day_page_list = []
    trimmed_day_page_list = []
    
    # creating the full range of day_page links
    for year in year_list:
        if year % 4 == 0:
            leap_year = True
        else:
            leap_year = False  
        for month in month_days:
            if month[0]==2 and leap_year: #check if it's a leap_year
                month = (2, 29)
            for day in range(1, month[1]+1):
                url = day_page_url_generator(year, month[0], day)
                one_date = date(year, month[0], day)
                day_order += 1
                response = (one_date, DayPage(url, one_date, day_order)) # making a tuple with the date and day page object
                full_day_page_list.append(response) # adding it to the list of day page objects    
                           
    # taking the specific day page links requested, or all of them if no range is specified
    today = date.today() # setting a today variable with the current year, month, and day
    if start:
        start = date(start['year'], start['month'], start['day'])
    else:
        start = date(2001, 11, 18)  
    if end:
        end = date(end['year'], end['month'], end['day'])
    else:
        end = date(today.year, today.month, today.day)

    # ensure start_date is before end_date
    assert start <= end, "start date must be before end date"
    
    started = False
    final_day_page_list = []
    for page in full_day_page_list:
        if page[0] == start:
            started = True
        if started:
            trimmed_day_page_list.append(page[1])
            if page[0] == end:
                return trimmed_day_page_list

def one_drudge_page_dump():
    ''' scrapes the most recent drudge page in the archive, outputs the results
    to a .csv file '''
    day_page_list = day_page_list_generator()
    sample_drudge_pages = day_page_list[0].day_page_scraper() # scrape it, get a list of drudge page objects
    sample_drudge_page =  sample_drudge_pages[-1] # grab the most recent drudge page object
    drudge_link_objects = sample_drudge_page.drudge_page_scraper() # scrape it, get drudge link objects
    with open('drudge_page.csv', 'w') as page:
        writer = csv.writer(page)
        
        for test in drudge_link_objects:
            writer.writerow(test.list_dump())
    return drudge_link_objects

def iterate_dump():
    # generate a list of day_pages within start and end dates, if given
    start_date = {'year': 2014, 'month':02, 'day': 25}
    end_date = {'year':2014, 'month':02, 'day': 25}
    day_pages = day_page_list_generator(start=start_date, end=end_date) 
    header_row = ['linkid', 'url', 'hed', 'main', 'splash', 'year', 'month', 'day', 'day_order', 'time']    
    #open a connection a .csv file to dump the data
    with open('drudge_page.csv', 'w') as page:
        writer = csv.writer(page)   
        writer.writerow(header_row)
        link_id = 1
        # iterate through my list of day pages
        for day_page in day_pages:
            #scrape each day page
            drudge_pages = day_page.day_page_scraper()
            i=1
            #iterate through my list of drudge_pages
            for drudge_page in drudge_pages:
                #scrape each drudge page for drudge_links
                drudge_links = drudge_page.drudge_page_scraper()
                print i, "out of", len(drudge_pages)
                i+=1
                #iterate through each drudge page's drudge links, write data to .csv file
                for link in drudge_links:                   
                    writer.writerow(link.list_dump())
               

def main_splash_tester():
    filename = 'sample_drudge_page.htm'
    #def __init__(self, url_obj, drudge_date, day_order):
    #def __init__(self, day_page_obj, url, time):
    made_up_day = DayPage(Url(filename), '2014-01-01', 1)
    drudge_page = DrudgePage(made_up_day, filename, "00:00:00")
    
    drudge_page_scraped = drudge_page.drudge_page_scraper()
    '''
    filename = 'sample_drudge_page.htm'
    with open(filename, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    top = soup.find(id='drudgeTopHeadlines')
    top = top.find_all('a')
    top = [link.text.encode('utf-8') for link in top]
    splash = ""
    splash = top.pop()
    main = set(top)
    print splash
    print
    print main
'''

def scraper():
    ''' This should get all the info we want for days, pages, and links.
        This version should output days, one page, and that page worth
        of links to .csv files. '''
    day_pages = day_page_list_generator()
    dump_day_pages_to_file(day_pages, 'days.csv')
    test

if __name__ == "__main__":
    scraper()


    '''
    #set a start and end date
    start_date = {'year': 2014, 'month':2, 'day':21}
    end_date = {'year': 2014, 'month':2, 'day': 21}
    #iterate_dump()
    one_drudge_page_dump()
    '''
         
