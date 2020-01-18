import json
from datetime import timedelta, date


# Helper Function returns the odds of a specific horse
# TODO: Improve to maybe aggregate odds
def odds_return(horse):
    try:
        return horse['fixedOdds']['returnWin']
    except KeyError:
        return horse['parimutuel']['returnWin']


# Helper Function returns the odds of a specific horse
# TODO: Improve to maybe aggregate odds
def para_odds_return(horse):
    try:
        return horse['parimutuel']['returnWin']
    except KeyError:
        return horse['fixedOdds']['returnWin']


# Helper Function returns the odds of a specific horse
# TODO: Improve to maybe aggregate odds
"""def odds_return(horse, odds_type):
    if odds_type == 'fixed':
        try:
            return horse['fixedOdds']['returnWin']
        except KeyError:
            return horse['parimutuel']['returnWin']
    else:
        try:
            return horse['parimutuel']['returnWin']
        except KeyError:
            return horse['fixedOdds']['returnWin']"""


# Place wager on a race and determine outcome
def place_bet(horse, amount, race_info, bonus_bet):
    print('Wagered ' + str(amount) + ' on horse number ' + str(horse['runnerNumber']))
    # print(horse)
    # print(raceInfo['results'])
    # In this case we won the wager
    if horse['runnerNumber'] in race_info['results'][0]:
        if bonus_bet:
            print('We have a winning bonus bet')
            print('Horse Number ' + str(horse['runnerNumber']) + ' won ' + str((amount * odds_return(horse)) - amount))
            return (amount * odds_return(horse)) - amount, 'W'
        print('We have a winner!')
        print('Horse Number ' + str(horse['runnerNumber']) + ' won ' + str(amount * odds_return(horse)))
        return amount * odds_return(horse), 'W'
    # In this case we placed, but didn't win outright
    # TODO: Handle bonus bets
    if bonus_bet is True:
        print("There was no payout from the bonusBet")
        return 0, 'L'
    for placer in race_info['results'][1:]:
        if horse['runnerNumber'] in placer:
            print('We have a placer!')
            print('Horse Number ' + str(horse['runnerNumber']) + ' placed ' + str(
                amount * odds_return(horse)))
            return wager, 'P', horse
    # In this case we lost
    return 0, 'L'


# Calculates the wager amount
def calculate_wager(proj_win, horse_odds):
    return proj_win / horse_odds


# Bonus bet info should be Location, RaceNo, Date, Amount
def buildBonus(location, race_no, date, amount):
    return location, race_no, date, amount


print('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(4)).isoformat() + '.txt')
test_file = open(
    'D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(4)).isoformat() + '.txt', 'r')

walletBalance = 100
wagerCount = 0
totalWinnings = 0.0
bonusBets = []

for meeting in json.load(test_file):
    # if meeting['meetingName'] in ['RANDWICK', 'EAGLE FARM', 'MOONEE VALLEY']:
    if isinstance(meeting['meetingName'], str):
        # Gets the largest number in the key list (AKA number of races)
        print("The total number of races is " + str(int(max(filter(str.isnumeric, (meeting.keys()))))))
        print(filter(str.isnumeric, (meeting.keys())))
        for item in filter(str.isnumeric, (meeting.keys())):
            print(item)
        for raceNo in filter(str.isnumeric,
                             (meeting.keys())):  # range(1, int(max(filter(str.isnumeric, (meeting.keys())))) + 1):
            if int(raceNo) > 3:
                continue
            print(meeting[str(raceNo)])
            raceMeet = meeting[str(raceNo)]
            print("Race Number " + str(raceNo))
            # print(raceMeet.keys())
            # print(raceMeet['races'][str(raceNo)]['runners'])
            if raceMeet['races'][str(raceNo)]['raceStatus'] == 'Abandoned':
                print("Race number " + str(raceNo) + " was abandoned")
                continue
            # TODO: Accept races which don't have fixed odds
            print(raceMeet['races'][str(raceNo)]['hasFixedOdds'])
            if raceMeet['races'][str(raceNo)]['hasFixedOdds'] == 'False':
                print("Race number " + str(raceNo) + " has no fixed odds")
                continue
            scratchings = []
            for item in raceMeet['races'][str(raceNo)]['scratchings']:
                scratchings.append(item['runnerNumber'])
            print("Scratchings " + " ".join(map(str, scratchings)))
            runners = []
            for horse in raceMeet['races'][str(raceNo)]['runners']:
                if int(horse['runnerNumber']) in scratchings:
                    continue
                print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                # print(horse['parimutuel']['returnWin'])
                # if new_dict['races'][str(num)]
                # print(horse['fixedOdds']['returnWin'])
                runners.append(horse)
            print("Runners " + " ".join(map(str, runners)))
            runners.sort(key=para_odds_return)
            runners.sort(key=odds_return)
            for horse in runners:
                print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                print(horse['parimutuel']['returnWin'])
                # if new_dict['races'][str(num)]
                print(horse.get('fixedOdds', {}).get('returnWin'))
            # print(runners)
            # Aim to make the profits of the first horse
            projWin = float(odds_return(runners[0]))
            totalWageredAmt = 0.0
            print("The projected winning is " + str(projWin) + " on horse number " + str(runners[0]['runnerNumber']))
            print(runners[0]['runnerNumber'])
            print(raceMeet['races'][str(raceNo)])
            # Places cash bets
            if bonusBets:
                print(bonusBets)
                currentBB = bonusBets.pop(0)
                wager = place_bet(runners[0], currentBB[3], raceMeet['races'][str(raceNo)], True)
                if wager[1] == 'W':
                    walletBalance += wager[0]
            while totalWageredAmt < projWin and runners:
                print(runners)
                wager = calculate_wager(projWin, odds_return(runners[0]))
                print(wager)
                walletBalance -= wager
                totalWageredAmt += wager
                wagerCount += 1
                print('Total wagered amount is ' + str(totalWageredAmt))
                wager = place_bet(runners.pop(0), wager, raceMeet['races'][str(raceNo)], False)
                print(str(wager) + ' is the result')
                if wager[1] == 'W':
                    walletBalance += wager[0]
                    totalWinnings += wager[0]
                elif wager[1] == 'P':
                    # Promos tend to be first few races
                    if int(raceNo) < 4:
                        bonusBets.append(buildBonus(meeting['meetingName'], raceNo, meeting['date'], wager[0]))
                print(walletBalance)
            print('Total number of Bonus Bets is ' + str(len(bonusBets)))
            print(bonusBets)
            print(len(bonusBets))
            print("My wallet balance is " + str(walletBalance))
            print("The total wagers is " + str(wagerCount))
            print("The total winnings is " + str(totalWinnings))
