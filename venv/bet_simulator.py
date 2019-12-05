import json
from datetime import timedelta, date

print('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt')
test_file = open('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt', 'r')
for dict in json.load(test_file):
    if dict['meetingName'] == 'GRAFTON':
        print(dict['1'])