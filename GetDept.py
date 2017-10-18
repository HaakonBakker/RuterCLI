import requests
from prettytable import PrettyTable
import os
import sys
import re
from datetime import datetime
import time

# p GetDept.py FOP w

# Default departure = Forskningsparken (3010370)
dept = "3010370"
stopp = "Forskningsparken"
direction = "all"
defaultTimeTableLength = 8
if (len(sys.argv) >= 2):
    arg1 = str(sys.argv[1].lower()) # Dept Station
    # Check for Blindern
    if arg1 == "bli":
        dept = "3010360"
        stopp = "Blindern"
    if arg1 == "blindern":
        dept = "3010360"
        stopp = "Blindern"
    if arg1 == "nyd":
        dept = "3012130"
        stopp = "Nydalen"
    if arg1 == "nydalen":
        dept = "3012130"
        stopp = "Nydalen"

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

#print(deptInfo)

# Header = FOP
# Create a list of Line - Destination - Time
print("From: {}".format(stopp))

# Print the departures to the console
# http://reisapi.ruter.no/StopVisit/GetDepartures/3010370

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
    carriages = (deptInfo[counter]['MonitoredVehicleJourney']['TrainBlockPart']['NumberOfBlockParts'])
    carriagesText = "🚃  🚃"
    if carriages == "6":
        carriagesText = "🚃  🚃"
    elif carriages == "3":
        carriagesText = "🚃  "

    t.add_row([line, dest, sanntid ,timeForTable, carriagesText])
    counter += 1

t.align["Destination"] = "l"
print(t)
