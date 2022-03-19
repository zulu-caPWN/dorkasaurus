# from https://github.com/zulu-caPWN/attack-team-code/blob/master/dorkasaurus2.py

"""

To edit on each run

headers
header -> ua.random #replace the user agent value with this

paramsGet
take out the first query
q -> replace query value with the var dork

linkDict domain -> current domain ur dorking

proxy IP's

sleep

"""


import requests
from pymongo import MongoClient
import time
from itertools import cycle
from fake_useragent import UserAgent

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.dorks  # db name
cursor = db.exploitdb  # collection name
fg = cursor.find()
dorks = []
for each in fg:
    dorks.append(each['Dork'].encode("UTF-8"))
how_many_dorks = len(dorks)

# connect to dorkasaurus db to log found dorks
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.dorkasaurus_results  # db name
cursor = db.dorks_detected  # collection namefake_useragent
mongod_path = 'C:\Users\PK\Desktop\VM_Shared_Folder\mongodata'

dork_num = 0
dorks_detected = 0

session = requests.Session()
num_responses = 0

# UA #
ua = UserAgent()

# PROXIES #
# below are real proxies
# proxies = ['http://haha:haha@178.128.7.173:3128']
#below is burp testing proxy
proxies = ['http://127.0.0.1:8080']
proxy_pool = cycle(proxies)

#same as public cse url, doesnt seem to change
referer = 'https://cse.google.com/cse?cx=017068176148634300635:h_sgrss1jeo'
cx = referer.split('cx=')[1]
cse_tok = 'AOuiMRaWBxeHV_CAcJAzZm1dD89J:1542023837528' #dunno where this comes from
callback = 'google.search.Search.csqr8825'
target_domain = 'synology.com'

#goog send multiple reqs, it's usually the one where the get rq starts with /customsearch/v1element
for dork in dorks:
    proxy = next(proxy_pool)
    #replace user-agent value with ua.random
    headers = {"Accept": "*/*", "User-Agent": ua.random,
               "Referer": referer,
               "Connection": "close", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}

    paramsGet = {'cx': cx, 'cse_tok': cse_tok, 'callback': callback, 'q': dork}

    #below is old known working from a few months ago, not sure this would still work, keeing til we have a new working version
    # paramsGet = {"prettyPrint": "false", "hl": "en", "cse_tok": "ABPF6Hit_cWaeghITVwCYT7_LmDjHm9H0g:1526791686524",
    #              "gss": ".com", "num": "10", "googlehost": "www.google.com",
    #              "gs_l": "partner-generic.3...249851.249851.0.250510.1.1.0.0.0.0.0.0..0.0.gsnos,n=13...0.3j9j2..1ac.2.25.partner-generic..1.0.0.",
    #              "source": "gcsc", "sort": "", "sig": "c2209932f49d54b1ddc575672079011e", "q": dork,
    #              "cx": "017068176148634300635:h_sgrss1jeo", "rsz": "filtered_cse",
    #              "callback": "google.search.Search.apiary19300", "key": "AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY"}

    #  old version
    # response = session.get("https://www.googleapis.com/customsearch/v1element", params=paramsGet, headers=headers, proxies={'http':proxy, 'https':proxy})
    response = session.get("https://cse.google.com/cse/element/v1", params=paramsGet, headers=headers, proxies={'http':proxy, 'https':proxy}, verify=False)

    # below doesn't work, it uses json now
    try:
        num_responses = int(response.text.split('"estimatedResultCount":')[1].split(',')[0].split('"')[1])
    except Exception as e:
        print 'EXCEPTION!!!!!!!', e
        pass

    if num_responses >= 1:
        linkDict = {'domain': target_domain,
                    'dork_used': dork.strip(),
                    'dork_found': True,
                    'dork_list_ver': str(0.1)}
        # newList.append(linkDict)
        print target_domain, 'Dorked ->', dork
        posts = cursor.insert_one(linkDict)  # insert into db
        linkDict = {}
        dorks_detected += 1
        # print link

    else:
        print 'Failed dork', dork
        #print 'No DOrk Detected'
        #print
    dork_num += 1

    print 'RESPONSE TEXT\n', response.text
    #print dork


    #time.sleep(10)
    #print "Response body: %s" % response.content
    print 'Proxy', proxy
    #print response.request.headers['User-Agent']


    """Test for blocking by google"""
    #bad_proxies = set([])
    if response.status_code != 200:
        print 'BAD PROXIES!!!!!', proxy

    print 'Dorks remaining: ', str(how_many_dorks)
    how_many_dorks -= 1
    print 'Dorks detected: ', dorks_detected
    print "Response Status code:   %i" % response.status_code

    print '***********'
    print

    #below is sleep when using 8 proxies
    #time.sleep(.37) #sleep .5 worked, now trying .37, next .25
    # below using 1 proxy so we slowing it down
    time.sleep(4)