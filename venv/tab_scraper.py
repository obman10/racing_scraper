import requests
from requests import Request, Session
import json
import time
from datetime import timedelta, date
import mysql.connector


class meeting:
    def __init__(self, meetingname, meetingtype, meetingdate):
        self.meetingName = meetingname
        self.meetingType = meetingtype
        self.meetingDate = meetingdate
        self.meetingID = None

    def __str__(self):
        return "Meeting name is %s, meeting type is %s, meeting date is %s, meetingID is %s"\
               % (self.meetingName, self.meetingType, self.meetingDate, self.meetingID)

    def get_ID(self, dbconn):
        meeting_cursor = dbconn.cursor()
        select_meeting = ("SELECT meetingID FROM meeting "
                          "WHERE date = %s"
                          "AND meetingName = %s"
                          "AND meetingType = %s")
        meeting_cursor.execute(select_meeting, (self.meetingDate, self.meetingName, self.meetingType,))
        #print(meeting_cursor.rowcount)
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


class race:
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
                          "WHERE meetingID = %s"
                          "AND raceNumber = %s")
        race_cursor.execute(select_race, (self.meetingDate, self.raceNumber))
        # print(meeting_cursor.rowcount)
        results = meeting_cursor.fetchall()
        if results:
            for result in results:
                self.meetingID = result[0]
        else:
            self.meetingID = self.add_meeting(dbconn)
        return self.meetingID

def consume_races(races, meetingid):
    print(races)
    for race_obj in races["races"]:
        race(meetingid, race_obj)
    return None

def consume_futures(race_day, dbconn):
    meetings = []
    for meet in race_day["meetings"]:
        print(meet)
        print(meet.keys())
        new_meet = meeting(meet["meetingName"], meet["raceType"], meet["meetingDate"])
        new_meet.get_ID(dbconn)
        meetings.append(new_meet)
        try:
            #print(meet["_links"])
            consume_races(json.loads(requests.get(meet["_links"]["races"]).text), new_meet.meetingID)
        except KeyError:
            print(meet["meetingName"], "didn't seem to have a link onwards")
        break
    for meet in meetings:
        print(meet)
    return None


all_futures = requests.get("https://api.beta.tab.com.au/v1/tab-info-service/racing/dates?jurisdiction=VIC")
print(all_futures)
print(all_futures.text)
my_json = json.loads(all_futures.text)
mydb = mysql.connector.connect(host="localhost",
                               user="chris",
                               password="th30bs00",
                               database="racing")
for race_day in my_json["dates"]:
    print(race_day)
    r2 = requests.get(url=race_day["_links"]["meetings"])
    print(r2.text)
    consume_futures(json.loads(r2.text), mydb)
    break
