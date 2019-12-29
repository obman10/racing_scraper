import json
from datetime import timedelta, date


# Helper Function returns the odds of a specific horse
# TODO: Improve it to return para and fixed odds
def oddsReturn(horse):
    return horse['fixedOdds']['returnWin']


# Place wager on a race and determine outcome
def placeBet(horse, amount, raceInfo):
    print('Wagered ' + str(amount) + ' on horse number ' + str(horse['runnerNumber']))
    # print(horse)
    # print(raceInfo['results'])
    # In this case we won the wager
    if horse['runnerNumber'] in raceInfo['results'][0]:
        print('We have a winner!')
        print('Horse Number ' + str(horse['runnerNumber']) + ' won ' + str(amount * horse['fixedOdds']['returnWin']))
        return amount * horse['fixedOdds']['returnWin'], 'W'
    # In this case we placed, but didn't win outright
    # TODO: Handle bonus bets
    for placer in raceInfo['results'][1:]:
        if horse['runnerNumber'] in placer:
            print('We have a placer!')
            print('Horse Number ' + str(horse['runnerNumber']) + ' placed ' + str(
                amount * horse['fixedOdds']['returnWin']))
            return (wager, 'P', horse)
    # In this case we lost
    return (0, 'L')


# Calculates the wager amount
def calculateWager(projWin, horseOdds):
    return projWin / horseOdds

#Bonus bet info should be Location, RaceNo, Date, Amount
def buildBonus(location, raceNo, date, amount):
    return (location, raceNo, date, amount)


print('D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt')
test_file = open(
    'D:/PycharmProjects/racing_scraper/venv/historical_data_' + (date.today() - timedelta(3)).isoformat() + '.txt', 'r')

walletBalance = 100
wagerCount = 0
totalWinnings = 0.0
bonusBets = []

for meeting in json.load(test_file):
    # Currently having issues with no odds for ALBANY
    if meeting['meetingName'] == 'ALBANY':
    #if isinstance(meeting['meetingName'], str):
        # Gets the largest number in the key list (AKA number of races)
        print("The total number of races is " + str(int(max(filter(str.isnumeric, (meeting.keys()))))))
        print(filter(str.isnumeric, (meeting.keys())))
        for item in filter(str.isnumeric, (meeting.keys())):
            print(item)
        for raceNo in filter(str.isnumeric, (meeting.keys())):#range(1, int(max(filter(str.isnumeric, (meeting.keys())))) + 1):
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
                #print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                #print(horse['parimutuel']['returnWin'])
                # if new_dict['races'][str(num)]
                #print(horse['fixedOdds']['returnWin'])
                runners.append(horse)
            print("Runners " + " ".join(map(str, runners)))
            runners.sort(key=oddsReturn)
            for horse in runners:
                print(str(horse['runnerNumber']) + ' ' + horse['runnerName'])
                print(horse['parimutuel']['returnWin'])
                # if new_dict['races'][str(num)]
                print(horse['fixedOdds']['returnWin'])
            # print(runners)
            # Aim to make the profits of the first horse
            projWin = float(runners[0]['fixedOdds']['returnWin'])
            totalWageredAmt = 0.0
            print("The projected winning is " + str(projWin) + " on horse number " + str(runners[0]['runnerNumber']))
            print(runners[0]['runnerNumber'])
            # print(raceMeet['races'][str(raceNo)])
            while totalWageredAmt < projWin:
                print(runners)
                wager = calculateWager(projWin, runners[0]['fixedOdds']['returnWin'])
                print(wager)
                walletBalance -= wager
                totalWageredAmt += wager
                wagerCount += 1
                print('Total wagered amount is ' + str(totalWageredAmt))
                wager = placeBet(runners.pop(0), wager, raceMeet['races'][str(raceNo)])
                print(str(wager) + ' is the result')
                if wager[1] == 'W':
                    walletBalance += wager[0]
                    totalWinnings += wager[0]
                elif wager[1] == 'P':
                    #Promos tend to be first few races
                    if int(raceNo) < 5:
                        bonusBets.append(buildBonus(meeting['meetingName'], raceNo, meeting['date'],wager[0]))
                print(walletBalance)
            print('Bonus Bets')
            print(bonusBets)
            print(len(bonusBets))
            print("My wallet balance is " + str(walletBalance))
            print("The total wagers is " + str(wagerCount))
            print("The total winnings is " + str(totalWinnings))
