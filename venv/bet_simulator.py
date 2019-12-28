import json
from datetime import timedelta, date


def oddsReturn(horse):
    return (horse['fixedOdds']['returnWin'])


# Place wager on a race and determine outcome
def placeBet(horse, amount, raceInfo):
    print('Wagered 50')
    print(horse)
    print(raceInfo['results'])
    for placer in raceInfo['results']:
        if horse['runnerNumber'] in placer:
            print('We have a winner!')
            return (amount*horse['fixedOdds']['returnWin'])
    return (50, 'L')


print('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt')
test_file = open(
    'D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt', 'r')

walletBalance = 500.0

for meeting in json.load(test_file):
    if meeting['meetingName'] == 'BALLINA':
        # Gets the largest number in the key list (AKA number of races)
        print(int(max(filter(str.isnumeric, (meeting.keys())))))
        for raceNo in range(1, int(max(filter(str.isnumeric, (meeting.keys())))) + 1):
            print(meeting[str(raceNo)])
            raceMeet = meeting[str(raceNo)]
            print(raceMeet.keys())
            print(raceMeet['races'][str(raceNo)]['runners'])
            if raceMeet['races'][str(raceNo)]['raceStatus'] == 'Abandoned':
                print("Race number " + str(raceNo) + " was abandoned")
                continue
            scratchings = []
            for item in raceMeet['races'][str(raceNo)]['scratchings']:
                scratchings.append(item['runnerNumber'])
            print(scratchings)
            runners = []
            for horse in raceMeet['races'][str(raceNo)]['runners']:
                if int(horse['runnerNumber']) in scratchings:
                    continue
                print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                print(horse['parimutuel']['returnWin'])
                # if new_dict['races'][str(num)]
                print(horse['fixedOdds']['returnWin'])
                runners.append(horse)
            print(runners)
            runners.sort(key=oddsReturn)
            print(runners)
            projWin = float(runners[0]['fixedOdds']['returnWin'])*50
            wageredAmt = 0.0
            print(projWin)
            print(runners[0]['runnerNumber'])
            print(raceMeet['races'][str(raceNo)])
            #while wageredAmt <= projWin:
            #    walletBalance -= 50.0

            print(str(placeBet(runners[0], 50, raceMeet['races'][str(raceNo)])) + ' Was won')

