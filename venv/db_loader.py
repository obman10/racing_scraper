import json
import mysql.connector
import os

venv_dir = "C:/Users/chris/PycharmProjects/racing_scraper/venv"


# Loads in individual race meet
def meetingsloader(input_file, database_conn):
    meeting_cursor = database_conn.cursor()
    add_meeting = ("INSERT INTO meeting "
                   "(date, meetingName, meetingType) "
                   "VALUES (%s, %s, %s)")
    select_meeting = ("SELECT CAST(date AS CHAR), meetingName, meetingType FROM meeting "
                      "WHERE date = %s")
    # First build list of meetings
    meetings_list = []
    for meeting in input_file:
        race_date = meeting["date"]
        race_meet = meeting["meetingName"]
        for race in meeting.keys():
            # print(race)
            # print(meeting[race])
            if type(meeting[race]) is dict:
                for key in meeting[race].keys():
                    # print(key)
                    # print(meeting[race][key])
                    for key2 in meeting[race][key].keys():
                        # print(key2)
                        if type(meeting[race][key][key2]) is dict:
                            race_key_list = sorted(list(meeting[race][key][key2].keys()))
                            # print(race_key_list)
                            for item in race_key_list:
                                # print(item + "," + str(meeting[race][key][key2][item]))
                                if item == 'meeting':
                                    race_type = meeting[race][key][key2][item]["raceType"]
                                    meeting_info = (race_date, race_meet, race_type)
                                    if meeting_info not in meetings_list:
                                        meetings_list.append(meeting_info)
                            # for key3 in meeting[race][key][key2].keys():
                            # print(key3)
                            #    if key3 in ["runners","scratchings"]:
                            # print(meeting[race][key][key2][key3])
                            #        for runner in meeting[race][key][key2][key3]:
                            #            print(runner)
        ##print(meeting)
        ##print(meeting['meetingName'])
        # meeting_info = (race_date, race_meet, race_type)
        # print(meeting_info)
        # meetingCursor.execute(add_meeting, meeting_info)
        # print(sorted(list(meeting.keys())))
        print(meetings_list)
    # Then check for meetings already in the meetings table
    print(meetings_list[0][0])
    meeting_cursor.execute(select_meeting, (meetings_list[0][0],))
    for db_return in meeting_cursor:
        print(db_return)
        if db_return in meetings_list:
            meetings_list.remove(db_return)
    print(meetings_list)
    # Then add the unknown meetings to the table
    if meetings_list:
        meeting_cursor.executemany(add_meeting, meetings_list)
        print(meeting_cursor.rowcount, "Record inserted successfully into Laptop table")
    else:
        print("No new rows added")
    database_conn.commit()
    meeting_cursor.close()


# Loads a single race to the DB
def racesloader(input_file, database_conn):
    race_cursor = database_conn.cursor()
    select_meetingID = ("SELECT meetingID from meeting "
                        "WHERE date = %s "
                        "AND meetingName = %s "
                        "AND meetingType = %s ")
    for meeting in input_file:
        race_date = meeting["date"]
        race_meet = meeting["meetingName"]
        for race in meeting.keys():
            print(race)
            print(meeting[race])
            if type(meeting[race]) is dict:
                for field in meeting[race].keys():
                    print(field)
                    print(meeting[race][field])
                    for key2 in meeting[race][field].keys():
                        # print(key2)
                        if type(meeting[race][field][key2]) is dict:
                            race_key_list = sorted(list(meeting[race][field][key2].keys()))
                            # print(race_key_list)
                            for item in race_key_list:
                                print(item + "," + str(meeting[race][field][key2][item]))
                                if item == 'meeting':
                                    race_type = meeting[race][field][key2][item]["raceType"]
                                    print(race_type)
                                    meeting_info = (race_date, race_meet, race_type)
                                    print(meeting_info)
                                    race_cursor.execute(select_meetingID, meeting_info)
                                    result = race_cursor.fetchall()

                                    assert len(result) is 1, "There are multiple results " + meeting_info
                                    print(result[0][0])
                                    #if meeting_info not in meetings_list:
                                    #    meetings_list.append(meeting_info)



mydb = mysql.connector.connect(host="localhost",
                               user="chris",
                               passwd="",
                               database="racing")
for file in os.listdir(venv_dir):
    if "historical_data" in file:
        print(file)
        the_file = open(venv_dir + "/" + file)
        historical_file = json.load(the_file)
        meetingsloader(historical_file, mydb)
        racesloader(historical_file, mydb)
        break

mydb.close()
