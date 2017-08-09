from models import DayPage, DrudgePage, DrudgeLink
from time import gmtime
import socket
from datetime import date, timedelta
import csv

DAY_PAGE_FMT_URL = "http://www.drudgereportarchives.com/data/%s/%02d/%02d/index.htm?s=flag"
START_DATE = date(2001, 11, 18)

def day_pages(start=START_DATE, end=date.today()):
    date_generator = (start + timedelta(days) for days in range((end-start).days))
    for dt in date_generator:
        url = DAY_PAGE_FMT_URL % (dt.year, dt.month, dt.day)
        yield DayPage(url, dt)

def scrape_archive():
    '''
    Iterates through a list of day pages, then fetches the drudge pages, then
    fetches the links. Creates DayPage objects, DrudgePage objects, and
    DrudgeLink objects. 

    For now it will write them all to a .csv file. Soon it will write them to
    a database where postprocessing and data analysis will be performed.

    '''
    # generate a list of day_pages within start and end dates, if given
    start_date = {'year': 2014, 'month':12, 'day': 7}
    end_date = {'year':2014, 'month':12, 'day': 7}
    day_pages = day_page_list_generator(start=start_date, end=end_date) 
    link_header_row = ['url',  'hed', 'top', 'splash',  'parent_drudge_page_id']
    day_page_header_row = []
    drudge_page_header_row = []    
    #open a connection a .csv file to dump the data
    with open('drudge_links.csv', 'w') as page:
        writer = csv.writer(page)   
        writer.writerow(link_header_row)
        for day in day_pages:
            #scrape each day page
            drudge_pages = day.scrape_day_page()
            #iterate through my list of drudge_pages
            for index, drudge_page in enumerate(drudge_pages):
                if index==1: break
                #scrape each drudge page for drudge_links
                drudge_links = drudge_page.scrape()

                print index, "out of", len(drudge_pages)
                #iterate through each drudge page's drudge links, write data to .csv file
                for link in drudge_links:   
                    print link.list_dump()      
         
                    #writer.writerow(link.list_dump())

