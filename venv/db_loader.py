import json
import os
import mysql.connector

venv_dir = "C:/Users/chris/PycharmProjects/racing_scraper/venv"

""" Direction to take the DB inserts
    I am willing to parse the files in more complicated ways to build lists then just have a single query for the list
    I once I pull from different sources then I want to be able to re use the insert functions and just have new list builders
"""


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
            if type(meeting[race]) is dict:
                for key in meeting[race].keys():
                    for key2 in meeting[race][key].keys():
                        if type(meeting[race][key][key2]) is dict:
                            race_key_list = sorted(list(meeting[race][key][key2].keys()))
                            for item in race_key_list:
                                if item == 'meeting':
                                    race_type = meeting[race][key][key2][item]["raceType"]
                                    meeting_info = (race_date, race_meet, race_type)
                                    if meeting_info not in meetings_list:
                                        meetings_list.append(meeting_info)
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
        print(meeting_cursor.rowcount, "Record inserted successfully into meetings table")
    else:
        print("No new rows added")
    database_conn.commit()
    meeting_cursor.close()


def raceBuilder():
    optimal_race_info = {}
    race_tuple = ()
    return race_tuple


# Build a proposition
def construct_proposition(id_tuple, runner, database_conn, scratches):
    prop_cursor = database_conn.cursor()
    #jockey = {"jockeyFirstName": runner["riderDriverName"].split(' ')[0],
    #          "jockeyLastName": runner["riderDriverName"].split(' ')[-1],
    #          "jockeyOtherName": None}
    select_proposition = ("SELECT propositionID FROM proposition "
                          "WHERE race_runnerID = %s "
                          "AND bookieID = %s "
                          "AND oddsType = %s ")
    prop_list = []
    prop_id = None
    # Can be expanded later to include exotics
    translator = {"fixedOdds" : "Fixed", "parimutuel" : "Parimutuel"}
    # Build a proposition for both the tote and the fixed
    proposition = {"race_runnerID" : race_runner_loader(database_conn, id_tuple[2], runner, scratches), "bookieID" : id_tuple[0], "oddsType" : None, "oddsWin" : None, "oddsPlace": None}
    for oddsType in ['fixedOdds', 'parimutuel']:
        if oddsType in runner.keys():
            try:
                proposition["oddsType"] = translator[oddsType]
                proposition["oddsWin"] = runner[oddsType]["returnWin"]
                proposition["oddsPlace"] = runner[oddsType]["returnPlace"]
            except KeyError:
                print("We had some error with no results in the odds section")
                print(proposition)
            prop_cursor.execute(select_proposition, (proposition["race_runnerID"], proposition["bookieID"], translator[oddsType]))
            for db_return in prop_cursor:
                print(db_return)
                prop_id = db_return[0]
            if not prop_id:
                prop_list.append(tuple(proposition.values()))
                print(proposition.values())
            else:
                print(prop_id, "No id needed.")

    # First we need to know the race_runnerID
    # This requires us to build a race_runner
    return prop_list


# Finds the Race Runner ID, or builds a new one
def race_runner_loader(db_connection, race_id, runner, scratches):
    race_runner_cursor = db_connection.cursor()
    add_race_runner = ("INSERT INTO race_runner "
                 "(raceID, jockeyID, horseID, barrierNumber, finishingPosition, runnerNumber, scratched) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    select_race_runner = ("SELECT race_runnerID FROM race_runner "
                    "WHERE raceID = %s "
                    "AND jockeyID = %s "
                    "AND horseID = %s ")
    jockey_id = None
    if runner["riderDriverName"]:
        jockey_id = jockey_loader(db_connection, {"jockeyFirstName": runner["riderDriverName"].split(' ')[0],
              "jockeyLastName": runner["riderDriverName"].split(' ')[-1]})
    horse_id = horse_loader(db_connection, {"horseName" : runner["runnerName"], "trainerName" : runner["trainerName"]})
    race_runner = {"raceID" : race_id, "jockeyID" : jockey_id, "horseID" : horse_id, "barrierNumber" : runner["barrierNumber"], "finishingPosition" : runner["finishingPosition"], "runnerNumber" : runner["runnerNumber"], "scratched" : False}
    for scratch in scratches:
        if scratch["runnerNumber"] == race_runner["runnerNumber"]:
            race_runner["scratched"] = True
    print(tuple(runner.values()))
    race_runner_id = None
    race_runner_cursor.execute(select_race_runner, (race_id, jockey_id, horse_id))
    for db_return in race_runner_cursor:
        print(db_return[0])
        race_runner_id = db_return[0]
    if not race_runner_id:
        race_runner_cursor.execute(add_race_runner, tuple(race_runner.values()))
        print(race_runner_cursor.lastrowid, "Record inserted successfully into race_runner table")
        db_connection.commit()
        race_runner_cursor.close()
        return race_runner_cursor.lastrowid
    else:
        print("No new rows added")
        race_runner_cursor.close()
    return race_runner_id


# Finds the Horse ID, or builds a new one
def horse_loader(db_connection, horse):
    horse_cursor = db_connection.cursor()
    add_horse = ("INSERT INTO horse "
                  "(horseName, trainerName) "
                  "VALUES (%s, %s)")
    select_horse = ("SELECT horseID FROM horse "
                     "WHERE horseName = %s"
                     "AND trainerName = %s")
    print(tuple(horse.values()))
    horse_id = None
    horse_cursor.execute(select_horse, tuple(horse.values()))
    for db_return in horse_cursor:
        print(db_return[0])
        horse_id = db_return[0]

    if not horse_id:
        horse_cursor.execute(add_horse, tuple(horse.values()))
        print(horse_cursor.lastrowid, "Record inserted successfully into horse table")
        db_connection.commit()
        horse_cursor.close()
        return horse_cursor.lastrowid
    else:
        print("No new rows added")
        print(horse_id, "horse id")
        horse_cursor.close()
    return horse_id


# Finds the jockey ID, or builds a new one
def jockey_loader(db_connection, jockey):
    jockey_cursor = db_connection.cursor(buffered=True)
    add_jockey = ("INSERT INTO jockey "
                   "(jockeyFirstName, jockeyLastName) "
                   "VALUES (%s, %s)")
    select_jockey = ("SELECT jockeyID FROM jockey "
                      "WHERE jockeyFirstName = %s"
                      "AND jockeyLastName = %s")
    print(tuple(jockey.values()))
    jockey_id = None
    jockey_cursor.execute(select_jockey, tuple(jockey.values()))
    for db_return in jockey_cursor:
        print(db_return[0])
        jockey_id = db_return[0]
    print(jockey_id)
    if not jockey_id:
        print("enter the not")
        jockey_cursor.execute(add_jockey, tuple(jockey.values()))
        print(jockey_cursor.lastrowid, "Record inserted successfully into jockey table")
        db_connection.commit()
        jockey_cursor.close()
        return jockey_cursor.lastrowid
    else:
        print("No new rows added")
        jockey_cursor.close()
    return jockey_id


# Builds a meeting then returns the ID
def meeting_loader(db_connection, meeting_construct):
    meeting_cursor = db_connection.cursor()
    add_meeting = ("INSERT INTO meeting "
                   "(date, meetingName, meetingType) "
                   "VALUES (%s, %s, %s)")
    select_meeting = ("SELECT meetingID FROM meeting "
                      "WHERE date = %s"
                      "AND meetingName = %s"
                      "AND meetingType = %s")
    print(tuple(meeting_construct.values()))
    meeting_id = None
    meeting_cursor.execute(select_meeting,
                           (meeting_construct["date"], meeting_construct["meetingName"], meeting_construct["raceType"]))
    for db_return in meeting_cursor:
        print(db_return[0])
        meeting_id = db_return[0]
    # Then add the unknown meetings to the table
    if not meeting_id:
        meeting_cursor.execute(add_meeting, tuple(meeting_construct.values()))
        print(meeting_cursor.lastrowid, "Record inserted successfully into meetings table")
        db_connection.commit()
        meeting_cursor.close()
        return meeting_cursor.lastrowid
    else:
        print("No new rows added")
        meeting_cursor.close()
    return meeting_id


# Returns a raceId and builds a new race if needed
def race_loader(db_conn, race_construct, race):
    race_cursor = db_conn.cursor(buffered=True)
    select_race = ("SELECT raceID FROM race "
                   "WHERE meetingID = %s "
                   "AND raceNumber = %s ")
    add_race = ("INSERT INTO race "
                "(meetingID, dividends, hasFixedOdds, raceName, raceNumber, raceStartTime, raceStatus, resultedTime, "
                "results, runners, scratchings, substitute, willHaveFixedOdds, hasParimutuel, meeting, pools, "
                "raceClassConditions, raceDistance) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    race_id = None
    race_cursor.execute(select_race, tuple(race_construct.values()))
    for db_return in race_cursor:
        print(db_return)
        race_id = db_return[0]
    if not race_id:
        race_cursor.execute(add_race, (race_construct["meetingID"],
                                       str(race["dividends"]),
                                       race["hasFixedOdds"],
                                       race["raceName"],
                                       race_construct["raceNumber"],
                                       race["raceStartTime"],
                                       race["raceStatus"],
                                       race["resultedTime"],
                                       str(race["results"]),
                                       str(race["runners"]),
                                       str(race["scratchings"]),
                                       race["substitute"],
                                       race["willHaveFixedOdds"],
                                       race["hasParimutuel"],
                                       str(race["meeting"]),
                                       str(race["pools"]),
                                       race["raceClassConditions"],
                                       race["raceDistance"]))
        print(race_cursor.lastrowid, "Record inserted successfully into race table")
        db_conn.commit()
        race_cursor.close()
        return race_cursor.lastrowid
    else:
        print("No new rows added")
        race_cursor.close()
    return race_id


def propositionloader(input_file, database_conn):
    prop_cursor = database_conn.cursor(buffered=True)
    insert_proposition = "INSERT INTO proposition (race_runnerID, bookieID, oddsType, oddsWin, oddsPlace)" \
                         "VALUES (%s, %s, %s, %s, %s)"
    select_bookie = "SELECT bookieID FROM bookie WHERE bookieName = %s"

    # Get bookie ID
    prop_cursor.execute(select_bookie, ("TAB",))
    cursor_ret = prop_cursor.fetchall()
    assert len(cursor_ret) is 1
    bookie_id = cursor_ret[0][0]
    proposition_list = []

    for meeting in input_file:
        #print(meeting)
        meeting_construct = {"date": meeting["date"], "meetingName": meeting["meetingName"], "raceType": None}
        meeting_id = None
        # The historical data from TAB has two nested racelists
        for outer_race in meeting.keys():
            #print("welcome to the outer race.")
            #print(outer_race)
            race_construct = {"meetingID": None, "raceNumber": outer_race}
            race_id = None
            if type(meeting[outer_race]) is dict:
                for summary_header in meeting[outer_race].keys():
                    #print(meeting[outer_race][summary_header])
                    #print(meeting[outer_race][summary_header].keys())
                    if summary_header == "races":
                        for race in meeting[outer_race][summary_header].keys():
                            #print(meeting[outer_race][summary_header][race])
                            #print(meeting[outer_race][summary_header][race].keys())
                            # Pass build meeting to the proposition constructor
                            if "meeting" in meeting[outer_race][summary_header][race].keys():
                                meeting_construct["raceType"] = meeting[outer_race][summary_header][race]["meeting"][
                                    "raceType"]
                            # print(meeting_construct)
                            # At this level we have the meeting information
                            if meeting_id is None:
                                meeting_id = meeting_loader(database_conn, meeting_construct)
                            # We now have enough information to build a race
                            race_construct["meetingID"] = meeting_id
                            race_id = race_loader(database_conn, race_construct,
                                                  meeting[outer_race][summary_header][race])
                            #print(race_id)
                            # Here is where the horses are stored
                            if "runners" in meeting[outer_race][summary_header][race].keys():
                                for runner in meeting[outer_race][summary_header][race]["runners"]:
                                    # print(runner)
                                    # print(runner.keys())
                                    assert "fixedOdds" or "parimutuel" in runner.keys()
                                    # print(runner["fixedOdds"])
                                    # print(runner["parimutuel"])
                                    # print("%s This is the bookie_id" % bookie_id)
                                    # print(runner["riderDriverName"])
                                    proposition_list.extend(
                                        construct_proposition((bookie_id, meeting_id, race_id), runner, database_conn, meeting[outer_race][summary_header][race]["scratchings"]))
            #print(outer_race)
            #print(meeting[outer_race])
        #print(proposition_list)
        #break
    # Here I can insert all the propositions for a single file
    prop_cursor.executemany(insert_proposition, proposition_list)
    print(prop_cursor.rowcount, "Records inserted successfully into proposition table")
    database_conn.commit()
    prop_cursor.close()
    return None


# Loads a single race to the DB
def racesloader(input_file, database_conn):
    race_cursor = database_conn.cursor(buffered=True)
    select_meetingID = ("SELECT meetingID from meeting "
                        "WHERE date = %s "
                        "AND meetingName = %s "
                        "AND meetingType = %s ")
    add_race = ("INSERT INTO race "
                "(meetingID, dividends, hasFixedOdds, raceName, raceNumber, raceStartTime, raceStatus, resultedTime, results, runners, scratchings, substitute, willHaveFixedOdds, hasParimutuel, meeting, pools, raceClassConditions, raceDistance) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    select_race = (
        "SELECT meetingID, dividends, hasFixedOdds, raceName, raceNumber, raceStartTime, raceStatus, resultedTime, results, runners, scratchings, substitute, willHaveFixedOdds, hasParimutuel, meeting, pools, raceClassConditions, raceDistance FROM race "
        "WHERE meetingID = %s "
        "AND raceNumber = %s ")
    for meeting in input_file:
        race_date = meeting["date"]
        race_meet = meeting["meetingName"]
        races_list = []
        horses_list = []
        jockey_list = []
        for race in meeting.keys():
            if type(meeting[race]) is dict:
                for field in meeting[race].keys():
                    for key2 in meeting[race][field].keys():
                        # print(key2)
                        if type(meeting[race][field][key2]) is dict:
                            race_key_list = list(meeting[race][field][key2].keys())
                            # print(race_key_list)
                            meeting_id = None
                            for item in race_key_list:
                                print(item + "," + str(meeting[race][field][key2][item]))
                                print(type(meeting[race][field][key2][item]))
                                if item == 'meeting':
                                    race_type = meeting[race][field][key2][item]["raceType"]
                                    print(race_type)
                                    meeting_info = (race_date, race_meet, race_type)
                                    # print(meeting_info)
                                    race_cursor.execute(select_meetingID, meeting_info)
                                    result = race_cursor.fetchall()
                                    assert len(result) is 1, "There are multiple results " + meeting_info
                                    print(result[0][0])
                                    meeting_id = result[0][0]
                            race_cursor.execute("SELECT * FROM race "
                                                "LIMIT 1 ")
                            race_cursor.fetchall()
                            if field == "races":
                                race_cursor.execute(select_race,
                                                    (meeting_id, meeting[race][field][key2]["raceNumber"],))
                                result = race_cursor.fetchall()
                                print(result)
                                if len(result) is 0:
                                    races_list.append((meeting_id, str(meeting[race][field][key2]["dividends"]),
                                                       meeting[race][field][key2]["hasFixedOdds"],
                                                       meeting[race][field][key2]["raceName"],
                                                       meeting[race][field][key2]["raceNumber"],
                                                       meeting[race][field][key2]["raceStartTime"],
                                                       meeting[race][field][key2]["raceStatus"],
                                                       meeting[race][field][key2]["resultedTime"],
                                                       str(meeting[race][field][key2]["results"]),
                                                       str(meeting[race][field][key2]["runners"]),
                                                       str(meeting[race][field][key2]["scratchings"]),
                                                       meeting[race][field][key2]["substitute"],
                                                       meeting[race][field][key2]["willHaveFixedOdds"],
                                                       meeting[race][field][key2]["hasParimutuel"],
                                                       str(meeting[race][field][key2]["meeting"]),
                                                       str(meeting[race][field][key2]["pools"]),
                                                       meeting[race][field][key2]["raceClassConditions"],
                                                       meeting[race][field][key2]["raceDistance"]))
                                    print(races_list)
                                    print(len(races_list))
                                    print("Its a good append!")
                                else:
                                    # Here I can start to add the horses and jockeys
                                    print("The race already existed.")
        print(races_list)
        if races_list:
            race_cursor.executemany(add_race, races_list)
            print(race_cursor.rowcount, "Records inserted successfully into races table")
        else:
            print("No new rows added")
        database_conn.commit()
    race_cursor.close()


mydb = mysql.connector.connect(host="localhost",
                               user="chris",
                               password="th30bs00",
                               database="racing")
for file in sorted(os.listdir('./Scraped_Data/'),reverse=True):
    if "historical_data" in file:
        print(file)
        the_file = open("./Scraped_Data/" + file)
        historical_file = json.load(the_file)
        # meetingsloader(historical_file, mydb)
        # racesloader(historical_file, mydb)
        propositionloader(historical_file, mydb)
mydb.close()
