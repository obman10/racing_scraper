import json
import mysql.connector

the_file = open("C:/Users/chris/PycharmProjects/racing_scraper/venv/historical_data_2020-02-17.txt")
file = json.load(the_file)
mydb= mysql.connector.connect(host="localhost",
                              user="chris",
                              passwd="Th30bs00@",
                              database="racing")
meetingCursor = mydb.cursor()
add_meeting =   ("INSERT INTO meeting " 
                "(date, meetingName) "
                "VALUES (%s, %s)")
for meeting in file:
    meeting_info = (meeting["date"], meeting["meetingName"])
    print(meeting_info)
    meetingCursor.execute(add_meeting, meeting_info)
    for race in meeting.keys():
        #print(race)
        #print(meeting[race])
        if type(meeting[race]) is dict:
            for key in meeting[race].keys():
                #print(key)
                #print(meeting[race][key])
                for key2 in meeting[race][key].keys():
                    #print(key2)
                    if type(meeting[race][key][key2]) is dict:
                        race_key_list = sorted(list(meeting[race][key][key2].keys()))
                        #print(race_key_list)
                        #for item in race_key_list:
                        #    print(item + "," + str(meeting[race][key][key2][item]))
                        #for key3 in meeting[race][key][key2].keys():
                            #print(key3)
                        #    if key3 in ["runners","scratchings"]:
                                #print(meeting[race][key][key2][key3])
                        #        for runner in meeting[race][key][key2][key3]:
                        #            print(runner)
    ##print(meeting)
    ##print(meeting['meetingName'])

    #print(sorted(list(meeting.keys())))
mydb.commit()
meetingCursor.close()
mydb.close()