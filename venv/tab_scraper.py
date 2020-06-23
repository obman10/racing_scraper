import requests
from requests import Request, Session
import json
import time
from datetime import timedelta, date, datetime
import mysql.connector


class meeting:
    tabCols = ('meetingID', 'venueID', 'date', 'meetingName', 'meetingType', 'createDate')

    def __init__(self, meetingname, meetingtype, meetingdate):
        self.meetingName = meetingname
        self.meetingType = meetingtype
        self.meetingDate = meetingdate
        self.meetingID = None
        print(self.tabCols)

    def __str__(self):
        return "Meeting name is %s, meeting type is %s, meeting date is %s, meetingID is %s" \
               % (self.meetingName, self.meetingType, self.meetingDate, self.meetingID)

    def get_ID(self, dbconn):
        meeting_cursor = dbconn.cursor()
        select_meeting = ("SELECT meetingID FROM meeting "
                          "WHERE date = %s"
                          "AND meetingName = %s"
                          "AND meetingType = %s")
        meeting_cursor.execute(select_meeting, (self.meetingDate, self.meetingName, self.meetingType,))
        # print(meeting_cursor.rowcount)
        results = meeting_cursor.fetchall()
        if results:
            for result in results:
                self.meetingID = result[0]
        else:
            self.meetingID = self.add_meeting(dbconn)
        return self.meetingID

    def add_meeting(self, dbconn):
        meeting_cursor = dbconn.cursor()
        add_meeting = ("INSERT INTO meeting "
                       "(date, meetingName, meetingType) "
                       "VALUES (%s, %s, %s)")
        meeting_cursor.execute(add_meeting, (self.meetingDate, self.meetingName, self.meetingType,))
        dbconn.commit()
        print(meeting_cursor.lastrowid)
        return meeting_cursor.lastrowid

    def set_cols(dbconn):
        meeting_cursor = dbconn.cursor()
        get_colnames = ("SELECT * FROM MEETING "
                        "LIMIT 1 ")
        meeting_cursor.execute(get_colnames)
        results = meeting_cursor.fetchall()
        print(meeting_cursor.column_names)
        tabCols = meeting_cursor.column_names
        meeting_cursor.close()


class race:
    tabCols = ('meetingID', 'dividends', 'hasFixedOdds', 'weather', 'raceName', 'raceNumber',
               'raceStartTime', 'raceStatus', 'resultedTime', 'results', 'runners', 'scratchings', 'substitute',
               'willHaveFixedOdds', 'hasParimutuel', 'meeting', 'pools', 'raceClassConditions', 'raceDistance')

    def __init__(self, meetingid, optional={}):
        self.meetingID = meetingid
        for k, v in optional.items():
            print(k, v)
            setattr(self, k, v)

    def __str__(self):
        return "Hello World"

    def get_ID(self, dbconn):
        race_cursor = dbconn.cursor()
        select_race = ("SELECT raceID FROM race "
                       "WHERE meetingID = %s "
                       "AND raceNumber = %s ")
        race_cursor.execute(select_race, (self.meetingID, self.raceNumber,))
        # print(meeting_cursor.rowcount)
        results = race_cursor.fetchall()
        if results:
            for result in results:
                self.raceID = result[0]
        else:
            self.raceID = self.add_race(dbconn)
        return self.raceID

    def add_race(self, dbconn):
        print("Start add_race")
        race_cursor = dbconn.cursor()
        insert_vals = []
        for column in self.tabCols:
            print(column + " " + str(getattr(self, column, None)))
            attr = getattr(self, column, None)
            if type(attr) is list:
                print("We found a list")
                insert_vals.append(str(attr))
            elif type(attr) in [str, int, bool]:
                print("else 1")
                # MYSQl doesnt support all ISO 8601 strings, namely Z time strings which TAB has sometimes.
                if column is 'raceStartTime':
                    insert_vals.append(datetime.fromisoformat(attr.replace("Z", "+00:00")))
                #Must cast my bools
                else:
                    print("else 2")
                    if type(attr) is str and attr.upper() in ["TRUE", "FALSE"]:
                        print("I've got an upper")
                        insert_vals.append(bool(attr))
                    else:
                        insert_vals.append(attr)
            elif attr is None:
                print("we found a none")
                insert_vals.append(attr)
            else:
                print(type(attr))
                insert_vals.append(str(attr))
        print(insert_vals)
        print(tuple(insert_vals))
        add_race = "INSERT INTO race (meetingID, dividends, hasFixedOdds, weather, raceName, raceNumber, " \
                   "raceStartTime, raceStatus, resultedTime, results, runners, scratchings, substitute, " \
                   "willHaveFixedOdds, hasParimutuel, meeting, pools, raceClassConditions, raceDistance) VALUES (%s, " \
                   "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        race_cursor.execute(add_race, (tuple(insert_vals)))
        dbconn.commit()
        print(race_cursor.lastrowid)
        return race_cursor.lastrowid




class raceRunner:
    def __init__(self, raceid, optional={}):
        self.raceID = raceid
        for k, v in optional.items():
            print(k, v)
            setattr(self, k, v)


def consume_races(races, meetingid, dbconn):
    print(races)
    race_list = []
    print("I started the race consumption")
    try:
        for race_obj in races["races"]:
            new_race = race(meetingid, race_obj)
            new_race.get_ID(dbconn)
            race_list.append(new_race)
    except KeyError:
        print("There is a key error")
        print("Usually this means that there is only one race captured")
        new_race = race(meetingid, races)
        new_race.get_ID(dbconn)
        race_list.append(new_race)
        print(type(races))
        print(races)
    return None


def consume_futures(race_day, dbconn):
    meetings = []
    for meet in race_day["meetings"]:
        # TODO Consume the futures
        if "Futures" in meet["meetingName"]:
            continue
        print(meet)
        print(meet.keys())
        # If statement saves unifying records later
        if "displayMeetingName" in meet.keys():
            new_meet = meeting(meet["displayMeetingName"].upper(), meet["raceType"], meet["meetingDate"])
        else:
            new_meet = meeting(meet["meetingName"].upper(), meet["raceType"], meet["meetingDate"])
        new_meet.get_ID(dbconn)
        meetings.append(new_meet)
        try:
            print(meet["_links"])
            consume_races(json.loads(requests.get(meet["_links"]["races"]).text), new_meet.meetingID, dbconn)
        except KeyError:
            print(meet["meetingName"], "didn't seem to have a _link onwards")
            try:
                for race in meet["races"]:
                    print(race)
                    consume_races(json.loads(requests.get(race["_links"]["self"]).text), new_meet.meetingID, dbconn)
            except KeyError:
                print("yo bitch")

        # break
    for meet in meetings:
        print(meet)
    return None


all_futures = requests.get("https://api.beta.tab.com.au/v1/tab-info-service/racing/dates?jurisdiction=VIC")
print(all_futures)
print(all_futures.text)
my_json = json.loads(all_futures.text)
mydb = mysql.connector.connect(host="localhost",
                               user="chris",
                               password="",
                               database="racing")
for race_day in my_json["dates"]:
    print(race_day)
    r2 = requests.get(url=race_day["_links"]["meetings"])
    print(r2.text)
    consume_futures(json.loads(r2.text), mydb)
    # break
