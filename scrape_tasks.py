from drudge_scraper import *
import csv

def extract_source(url):
    '''
    This function takes a url (i.e. www.developers.google.com/python/edu) and 
    extracts the host name (or domain, or server name, or whatever it's 
    called) (i.e google). It's definitely not guaranteed to be perfect. I'll
    have to check the results for things that shouldn't be there, like 'www' 
    '''
    
    try:
        hostname = re.search(r'[a-zA-Z0-9.]+', url).group()
        hostname_components = hostname.split(".")
        if len(hostname_components) == 3:
            domain = hostname_components[1]
        elif len(hostname_components) == 4:
            if len(hostname_components[3]) > 2:
                domain = hostname_components[2]
            else:
                domain = hostname_components[1]
        else:
            domain = hostname_components[0]
    except:
        return None
        
def auto_name_gen():
    '''
    system for taking domains and turning them into source name - 
    
    1. split data between perm links and headline links
    2. extract the domain name from each link
    3. if the domain name is in the list of perm links, assign the text of the link
       to that 
    '''
    if domain in perma_links:
        source = domain.text
        return source
        
        
def hundred_urls():
    return_list = list()
    with open('drudge_page.csv', 'r') as f:
        rows = list(csv.reader(f))[1:100]
    urls = [entry[0] for entry in rows]
    return urls
        
if __name__ == "__main__":
    sample = hundred_urls()
    for entry in sample:
        domain = extract_source(entry)
        print entry[:50], domain
