import requests
from requests import Request, Session
import json
import time

header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
param = {'jurisdiction': 'VIC'}

def driver():
    meets = getMeets()
    for meet in meets:
        print(meet)
        #print(meet.keys())
        #time.sleep(5)
        if '_links' in meet.keys():
            print(meet['_links'])
            print(meet['_links']['races'])
            getRaceInfo(meet)


def getMeets():
    meets = []
    cache = {'jurisdiction': 'VIC'}
    r = requests.get('https://api.beta.tab.com.au/v1/tab-info-service/racing/dates', cache)
    #print(r.url)
    #print(json.loads(r.text))
    for item in json.loads(r.text)['dates']:
        print(item)
        rn = requests.get(item['_links']['meetings'])
        print(json.loads(rn.text))
        for unit in json.loads(rn.text)['meetings']:
            print(unit)
            meets.append(unit)
    return meets

def getRaceInfo(race):
    for num in range(len(race['races'])):
        r = requests.get(race['_links']['races'].split('?')[0]+'/'+str((num+1)), param)
        print(json.loads(r.text))
    return

driver()
