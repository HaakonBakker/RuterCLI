import requests
from prettytable import PrettyTable
import os
import sys
import re
from datetime import datetime
import time
import json


# Will lookup the file
startTime = time.time()
path = os.path.dirname(os.path.realpath(__file__))
stopPath = path + "/stops.json"

with open(stopPath) as json_data:
    data = json.load(json_data)

stationFound = False
if (len(sys.argv) >= 2):
    arg1 = str(sys.argv[1].lower()) # Dept Station
    for item in data["ArrayOfStop"]["Stop"]:
        try:
            if item["ShortName"].lower() == arg1:
                dept = item["ID"]
                stopp = item["Name"]
                stationFound = True
            if item["Name"].lower() == arg1:
                dept = item["ID"]
                stopp = item["Name"]
                stationFound = True
        except KeyError:
                pass
else:
    print("Usage: python3 GetDept.py STATION (W/E).")
    sys.exit()

if not stationFound:
    print(sys.argv[1] + " was not found.")
    sys.exit()

endTime = time.time()

# Timing the lookup
#print("Tok: " + str((endTime-startTime)))

direction = "all"
defaultTimeTableLength = 8

if (len(sys.argv) == 3): #Want to check the direction of the trains
    arg2 = str(sys.argv[2].lower()) # Dept Station
    if arg2 == "w":
        direction = "w"
        defaultTimeTableLength = defaultTimeTableLength * 2
    if arg2 == "west":
        direction = "w"
        defaultTimeTableLength = defaultTimeTableLength * 2
    if arg2 == "e":
        direction = "e"
        defaultTimeTableLength = defaultTimeTableLength * 2
    if arg2 == "east":
        direction = "e"
        defaultTimeTableLength = defaultTimeTableLength * 2

# Get departures from Forskningsparken
url = "http://reisapi.ruter.no/StopVisit/GetDepartures/" + dept
resp = requests.get(url)

# Check for errors
if not resp.ok:
    print ("Something went wrong! {}".format(resp.status_code))
    SystemExit()

deptInfo = resp.json()

# Create a list of Line - Destination - Time
print("From: {}".format(stopp))

t = PrettyTable(["Line", "Destination", "Real Time", "Time", "Carriages"])
counter = 0

for i in range(defaultTimeTableLength):

    # Will check if the lines are going west or east
    dirRef = (deptInfo[counter]['MonitoredVehicleJourney']['DirectionRef'])
    trainDir = "all"
    if dirRef == "1":
        dirRef = "e"
    elif dirRef == "2":
        dirRef = "w"

    if direction != dirRef and len(sys.argv) == 3:
        counter += 1
        continue


    dest = (deptInfo[counter]['MonitoredVehicleJourney']['DestinationName'])
    line = (deptInfo[counter]['MonitoredVehicleJourney']['LineRef'])
    expTime = (deptInfo[counter]['MonitoredVehicleJourney']['MonitoredCall']['ExpectedDepartureTime'])
    inDate = expTime
    timeForTable = re.sub(r"\d\d\d\d-\d\d-\d\dT(\d\d:\d\d:\d\d)\+\d\d:\d\d", r"\1", inDate)

    realTimeSub = re.sub(r"(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)\+\d\d:\d\d", r"\1 \2", inDate)
    format = '%Y-%m-%d %H:%M:%S'
    deptTime = datetime.strptime(realTimeSub, format)
    nowTime = datetime.now()
    diff = deptTime - nowTime
    sanntid = re.sub(r"\d\:(\d\d\:\d\d)\.(?:\d+)", r"\1", str(diff))

    #11:09:01
    try:
        carriages = (deptInfo[counter]['MonitoredVehicleJourney']['TrainBlockPart']['NumberOfBlockParts'])
        carriagesText = "🚃  🚃"
        if carriages == "6":
            carriagesText = "🚃  🚃"
        elif carriages == "3":
            carriagesText = "🚃  "
    except TypeError as e:
        carriagesText = "--"


    t.add_row([line, dest, sanntid ,timeForTable, carriagesText])
    counter += 1

t.align["Destination"] = "l"
print(t)
