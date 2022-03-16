# trying to change the parse cause version 2 will no longer pass the html to the soup properly when using selenium
########################
# to do =
# check for cockblock
# click the link to re-do search and show omitted results

# add to the regex find of the string...
# if regex:
#    find element by text'repeat the search with the omitted results included'.click()


from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# import mechanize
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import re
from time import sleep
import random
from pymongo import MongoClient
import sys

# db connection
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.search_engine_scraper  # db name
cursor = db.search_results  # collection name
# mongod_path = 'C:\\Users\PK\Desktop\VM_Shared_Folder\mongodata'

# this string shows up on the last page of results
regex_string = re.compile(
    r'(In\sorder\sto\sshow\syou\sthe\smost\srelevant\sresults,\swe\shave\somitted\ssome\sentries\svery\ssimilar\sto\sthe\s)(\d+)')

# creates the browser object
# br = mechanize.Browser()
# br.addheaders = [('User-agent', 'Mozilla/5.0')]
# br.set_handle_robots(False)

binary = r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'  # selenium browser driver bin location
fp = webdriver.FirefoxProfile()  # firefox profile
driver = webdriver.Firefox()


# driver = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp,
#                            executable_path=r'C:\Users\PK\Desktop\VM_Shared_Folder\01Jan\instagram\geckodriver.exe')

# open browser in a non google property
random_start_url = ['https://twitter.com', 'http://yahoo.com', 'http://facebook.com']
random_start_url = random.choice(random_start_url)
driver.get(random_start_url)

# leftover from trying to set prefs to 100, give goog a chance to set cookies
google_url = 'https://google.com'
driver.get(google_url)
driver.refresh()

# base search url ,ready for search term
base_url = 'http://google.com/search?q='

dork_list = ['filetype:xls', 'filetype:pdf']
with open(r'C:\Users\PK\Desktop\VM_Shared_Folder\01Jan\dorkasaurus\dork_list.txt') as f:
    dorks = f.readlines()

target_domain_list = ['directv.com']
with open(r'C:\Users\PK\Desktop\VM_Shared_Folder\01Jan\dorkasaurus\domain_list.txt') as f:
    domains = f.readlines()

# search term, url encoded, now ready to append to base_url
raw_search_term = "site:directv.com filetype:pdf"
search_term = urllib.parse.quote_plus(raw_search_term)
hundred_results = '&num=100'  # add to end of search request
page_increment = 100  # helps move to next page, if below try/except works we set this to 100

# base_url + search_term, pass to browser GET request
full_url = base_url + str(search_term) + hundred_results

page = 1  # search results page number
result_number = 0  # set to 0 instead of 1 cause it's always off by 1, dont know why
start_results_at = 0  # used to go to next page of results
regex_match = False  # Prime the while loop below to run
newList = []  # create list to add dicts of search results to

###########################################
# start while loop
###########################################
while not regex_match:  # keep running until we see the regex match = True

    driver.get(full_url)  # conduct the search
    # print 'Sleeping'
    # sleep(10)

    html = driver.page_source  # get page source
    # html = unicode(html, errors='ignore') #skip??

    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find_all('div', {'class': 'g'})
    nav = soup.find_all('div', id='foot')

    for i in main_div:
        try:
            # print 'Page: ', str(page)
            # print 'Number: ',str(result_number)

            # title = i.find('h3', {'class': 'r'})
            # print 'Title: ',title.text

            link = i.find('h3', {'class': 'r'}).a['href']
            linkDict = {'searchTerm': raw_search_term,
                        'scraped_link': link,
                        'scraped': 0}
            newList.append(linkDict)
            print(link)

            result_number += 1
        except:
            continue

    print('Page: ', str(page))  # for logging, page we're on
    print(str(result_number), 'results:')  # for logging, # of results

    print('newList pre: ', newList)  # just to see, what we're inserting into db from this search result page
    print()
    posts = cursor.insert_many(newList)  # insert into db
    newList = []  # re-initialize an empty list ready for next search page's results
    returned_url = driver.current_url
    print('returned url: ', returned_url)

    regex_search = re.findall(regex_string,
                              html)  # search html source for 'we limited results' string. indicates last page
    if regex_search:
        regex_match = True  # if we find that string we set the loop to True, so it will stop
        print('Found Most relevant Results text, shutting down')

    start_results_at += page_increment  # preparing to append this to search string to GET the next N results. needs to be tied to
    # whether we set results to 100 or 10
    full_url = base_url + str(search_term) + '&num=' + str(page_increment) + '&start=' + str(
        start_results_at)  # prep to get next page of search results
    page += 1  # for logging, let's us know what page of results we're on

    sleep_time = random.randint(20, 60)  # sleep to be kind to Google
    print('Sleeping ' + str(sleep_time) + ' seconds')
    sleep(sleep_time)