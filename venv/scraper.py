import requests
from requests import Request, Session
import json
import time
from datetime import timedelta, date

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
param = {'jurisdiction': 'VIC'}


def driver():
    """meets = getMeets()
    for meet in meets:
        print(meet)
        #print(meet.keys())
        #time.sleep(5)
        if '_links' in meet.keys():
            print(meet['_links'])
            print(meet['_links']['races'])
            getRaceInfo(meet)"""
    log_file = open('history_scraper_log.txt', 'w')
    log_file.writelines("Beginning the scrape!\n")
    for single_date in [date.today() - timedelta(x) for x in range(580)]:
        # The try catch will exclude files that already exist
        try:
            f = open('Scraped_Data/Integrated/historical_data_' + single_date.isoformat() + '.txt', 'r')
            print("The file already exists")
            f.close()
            continue
        except IOError:
            print("File not existing")
        first_flag = False
        r = requests.get(
            'https://api.beta.tab.com.au/v1/historical-results-service/NSW/racing/' + single_date.isoformat(), param)
        print(r.status_code)
        if r.status_code == 404:
            continue
        test_file = open('Scraped_Data/historical_data_' + single_date.isoformat() + '.txt',
                         'w')
        log_file.writelines(single_date.isoformat() + '\n')
        if 'meetings' in json.loads(r.text).keys():
            for item in json.loads(r.text)['meetings']:
                if first_flag:
                    test_file.write(',')
                else:
                    test_file.write('[')
                    first_flag = True
                print(item)
                info_packet = {'date': item['meetingDate'], 'meetingName': item['meetingName']}
                for race in item['races']:
                    print(race)
                    if 'raceNumber' in race.keys():
                        raceNo = str(race['raceNumber'])
                        info_packet[raceNo] = {'headline': race, 'races': {}}
                        if '_links' in race.keys():
                            r = requests.get(race['_links']['self'], param)
                            print(r)
                            if r.status_code == 404:
                                print(404)
                                log_file.writelines(race['_links']['self'])
                                log_file.writelines(param)
                                continue
                            results = json.loads(r.text)
                            if 'raceNumber' in results.keys():
                                info_packet[raceNo]['races'][results['raceNumber']] = results
                            else:
                                info_packet[raceNo]['races'][results['raceNumber']] = 'No results found'
                                log_file.writelines(
                                    'There was no data found on ' + single_date.isoformat() + ' for race ' + race[
                                        '_links'])
                test_file.write(json.dumps(info_packet, sort_keys=True, indent=4))
                # readRace(race)
        test_file.write(']')
        test_file.close()
    log_file.close()


# Here we have redundant functions

def getMeets():
    meets = []
    cache = {'jurisdiction': 'VIC'}
    r = requests.get('https://api.beta.tab.com.au/v1/tab-info-service/racing/dates', cache)
    # print(r.url)
    # print(json.loads(r.text))
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
        r = requests.get(race['_links']['races'].split('?')[0] + '/' + str((num + 1)), param)
        print(json.loads(r.text))
    return


def readRace(race):
    if '_links' in race.keys():
        r = requests.get(race['_links']['self'], param)
        results = json.loads(r.text)
        print(results)
        print(results.keys())


driver()
