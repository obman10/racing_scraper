import json
from datetime import timedelta, date

print('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt')
test_file = open(
    'D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt', 'r')
for dict in json.load(test_file):
    if dict['meetingName'] == 'TAREE':
        #Gets the largest number in the key list (AKA number of races)
        print(int(max(filter(str.isnumeric, (dict.keys())))))
        for num in range(1,int(max(filter(str.isnumeric, (dict.keys()))))+1):
            print(dict[str(num)])
            new_dict = dict[str(num)]
            print(new_dict.keys())
            print(new_dict['races'][str(num)]['runners'])
            for horse in new_dict['races'][str(num)]['runners']:
                print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                print(horse['parimutuel']['returnWin'])
                print(horse['fixedOdds']['returnWin'])


# Place wager on a race and determine outcome
def placeBet(raceInfo, amount):
    return (50, 'L')
