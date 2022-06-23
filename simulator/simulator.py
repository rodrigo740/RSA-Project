from email.policy import default
from turtle import speed
from anyio import Any
import paho.mqtt.client as mqtt
import signal
import gpxpy
import gpxpy.gpx
import time
import multiprocessing
import json
import math
from collections import defaultdict
import geopy
import geopy.distance
from geographiclib.geodesic import Geodesic
import pyproj
import requests
import polyline


# speed / gas / checktime
sync_stats = {
    "100": [120, 60, 300],
    "101": []
}

const = pow(10, 7)

# G1
vals1 = {"speed": 100, "checkTime": 10, "groupID": -1}
vals2 = {"speed": 100, "checkTime": 10, "groupID": -1}
vals3 = {"speed": 100, "checkTime": 10, "groupID": -1}
vals4 = {"speed": 100, "checkTime": 10, "groupID": -1}

# G2
vals5 = {"speed": 100, "checkTime": 10, "groupID": -1}
vals6 = {"speed": 100, "checkTime": 10, "groupID": -1}
vals7 = {"speed": 100, "checkTime": 10, "groupID": -1}

valsList = [vals1, vals2, vals3, vals4, vals5, vals6, vals7]

mySurroudings2 = dict()
mySurroudings3 = dict()
mySurroudings4 = dict()
mySurroudings5 = dict()

mySurroudings6 = dict()
mySurroudings7 = dict()
mySurroudings8 = dict()


denmInfo2 = dict()
denmInfo3 = dict()
denmInfo4 = dict()
denmInfo5 = dict()

denmInfo6 = dict()
denmInfo7 = dict()
denmInfo8 = dict()


mySurroudings2 = defaultdict(lambda: [], mySurroudings2)
mySurroudings3 = defaultdict(lambda: [], mySurroudings3)
mySurroudings4 = defaultdict(lambda: [], mySurroudings4)
mySurroudings5 = defaultdict(lambda: [], mySurroudings5)

mySurroudings6 = defaultdict(lambda: [], mySurroudings6)
mySurroudings7 = defaultdict(lambda: [], mySurroudings7)
mySurroudings8 = defaultdict(lambda: [], mySurroudings8)


denmInfo2 = defaultdict(lambda: (), denmInfo2)
denmInfo3 = defaultdict(lambda: (), denmInfo3)
denmInfo4 = defaultdict(lambda: (), denmInfo4)
denmInfo5 = defaultdict(lambda: (), denmInfo5)

denmInfo6 = defaultdict(lambda: (), denmInfo6)
denmInfo7 = defaultdict(lambda: (), denmInfo7)
denmInfo8 = defaultdict(lambda: (), denmInfo8)


surroudingsList = [mySurroudings2, mySurroudings3,
                   mySurroudings4, mySurroudings5, mySurroudings6, mySurroudings7, mySurroudings8]


client2 = mqtt.Client(userdata=(mySurroudings2, denmInfo2, vals1))
client3 = mqtt.Client(userdata=(mySurroudings3, denmInfo3, vals2))
client4 = mqtt.Client(userdata=(mySurroudings4, denmInfo4, vals3))
client5 = mqtt.Client(userdata=(mySurroudings5, denmInfo5, vals4))

client6 = mqtt.Client(userdata=(mySurroudings5, denmInfo5, vals5))
client7 = mqtt.Client(userdata=(mySurroudings5, denmInfo5, vals6))
client8 = mqtt.Client(userdata=(mySurroudings5, denmInfo5, vals7))

clientsList = [client2, client3, client4, client5, client6, client7, client8]

simulatorClient = mqtt.Client()


def handler(signum, frame):
    print("\nDisconnecting Mqtt clients")
    client2.disconnect
    client3.disconnect
    client4.disconnect
    client5.disconnect

    client6.disconnect
    client7.disconnect
    client8.disconnect

    simulatorClient.disconnect
    exit(1)


signal.signal(signal.SIGINT, handler)

# The callback for when the client receives a CONNACK response from the server.


def on_connectSim(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        simulatorClient.subscribe("cams")
        simulatorClient.subscribe("leaders")


# The callback for when a PUBLISH message is received from the server.
def on_messageSim(client, userdata, msg):
    payload = json.loads(msg.payload)
    if 'leader' in payload:
        print("leader:" + str(payload["leader"]))


# The callback for when the client receives a CONNACK response from the server.


def on_connect2(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client2.subscribe("vanetza/out/cam")
        client2.subscribe("vanetza/in/cam")
        client2.subscribe("vanetza/in/denm")
        client2.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message2(client, userdata, msg):
    payload = json.loads(msg.payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "fields" in str_payload:
        # print(str_payload)

        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "management" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']
    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)

    # print(userdata)
    # print(payload)


# The callback for when the client receives a CONNACK response from the server.
def on_connect3(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client3.subscribe("vanetza/out/cam")
        client3.subscribe("vanetza/in/cam")
        client3.subscribe("vanetza/in/denm")
        client3.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message3(client, userdata, msg):
    payload = json.loads(msg.payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        print(str(payload))

        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]['originatingStationID']
        print(payload["fields"]["denm"]["management"]
              ["actionID"]['originatingStationID'])
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        print(str(payload))

        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']
    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)

# The callback for when the client receives a CONNACK response from the server.


def on_connect4(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client4.subscribe("vanetza/out/cam")
        client4.subscribe("vanetza/in/cam")
        client4.subscribe("vanetza/in/denm")
        client4.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message4(client, userdata, msg):
    payload = json.loads(msg.payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']
    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)


# The callback for when the client receives a CONNACK response from the server.
def on_connect5(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client5.subscribe("vanetza/out/cam")
        client5.subscribe("vanetza/in/cam")
        client5.subscribe("vanetza/in/denm")
        client5.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message5(client, userdata, msg):
    payload = json.loads(msg.payload)
    # print(payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']
    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)

# The callback for when the client receives a CONNACK response from the server.


def on_connect6(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client6.subscribe("vanetza/out/cam")
        client6.subscribe("vanetza/in/cam")
        client6.subscribe("vanetza/in/denm")
        client6.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message6(client, userdata, msg):
    payload = json.loads(msg.payload)
    # print(payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]
        ['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']

    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)

# The callback for when the client receives a CONNACK response from the server.


def on_connect7(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client7.subscribe("vanetza/out/cam")
        client7.subscribe("vanetza/in/cam")
        client7.subscribe("vanetza/in/denm")
        client7.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message7(client, userdata, msg):
    payload = json.loads(msg.payload)
    # print(payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]
        ['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']

    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)

# The callback for when the client receives a CONNACK response from the server.


def on_connect8(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client8.subscribe("vanetza/out/cam")
        client8.subscribe("vanetza/in/cam")
        client8.subscribe("vanetza/in/denm")
        client8.subscribe("vanetza/out/denm")

# The callback for when a PUBLISH message is received from the server.


def on_message8(client, userdata, msg):
    payload = json.loads(msg.payload)
    # print(payload)
    str_payload = str(payload)
    # if managment in payload == denm received else cam
    if "management" in str_payload:
        userdata[1][str(payload["fields"]["denm"]["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["fields"]["denm"]["management"]["actionID"]
        ['originatingStationID']
        userdata[2]["speed"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][0]
        userdata[2]["checkTime"] = sync_stats[str(
            payload["fields"]["denm"]["situation"]["eventType"]['causeCode'])][2]
    elif "denm" in str_payload:
        userdata[1][str(payload["management"]["actionID"]
                        ['originatingStationID'])] = ()
        userdata[2]["groupID"] = payload["management"]["actionID"]['originatingStationID']

    else:
        # == -1 means no group as been found
        if userdata[2]["groupID"] == -1:
            pos = (payload["latitude"],
                   payload["longitude"], payload["heading"])
            userdata[0][str(payload["stationID"])].append(pos)


def parseGPX(gpxFile):

    coordsList = []

    # Parsing an existing file:
    # -------------------------

    gpx_file = open(gpxFile, 'r')

    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordsList.append((point.latitude, point.longitude))

    return coordsList


def calcBearing(lat1, lon1, lat2, lon2):
    longitude1 = lon1
    longitude2 = lon2
    latitude1 = math.radians(lat1)
    latitude2 = math.radians(lat2)
    longDiff = math.radians(longitude2-longitude1)
    y = math.sin(longDiff)*math.cos(latitude2)
    x = math.cos(latitude1)*math.sin(latitude2) - \
        math.sin(latitude1)*math.cos(latitude2)*math.cos(longDiff)

    return (math.degrees(math.atan2(y, x))+360) % 360


def check(myInfo, otherInfo):
    res = False
    bearingToOtherCar = calcBearing(
        lat1=myInfo[0]/const, lon1=myInfo[1]/const, lat2=otherInfo[0]/const, lon2=otherInfo[1]/const)
    bearingOfThisCar = myInfo[2]
    relativeBearing = bearingToOtherCar - bearingOfThisCar
    if (relativeBearing < -180):
        relativeBearing = 360 + relativeBearing
    if (relativeBearing > 180):
        relativeBearing = 360 - relativeBearing

    if relativeBearing >= 170 and relativeBearing <= 190:
        res = True
    else:
        res = False

    return res


def leaderCheck(currClient, mySurroudings, currentLeader):

    # heading
    # north - 0
    # east - 90
    # west - 270
    # south 180
    res = False
    myInfo = mySurroudings[str(currClient)][len(
        mySurroudings[str(currClient)])-1]

    # print("myInfo: " + str(myInfo))

    if currentLeader != -1:
        # print("There is a leader: " + str(currentLeader) + " - " + str(currClient))
        otherInfo = mySurroudings[str(currentLeader)][len(
            mySurroudings[str(currentLeader)])-1]
        # print("otherInfo: " + str(otherInfo))

        return check(myInfo, otherInfo)
    # print("There isn't a leader: " + str(currClient))

    for key in mySurroudings:
        if key != str(currClient):
            otherInfo = mySurroudings[key][len(mySurroudings[key])-1]
            # print("otherInfo: " + str(otherInfo))

            res = check(myInfo, otherInfo)
            if not res:
                return res

    return res


def startSimul(currClient, startPoint, distances, bearings, stationType, mySurr, currentGroup, vals, sync_stats):
    print("Client: " + str(currClient) + " has started the simulation")

    # Connecting to the broker
    if currClient == 0:

        # OBU1 client
        client2.on_connect = on_connect2
        client2.on_message = on_message2

        client2.connect("192.168.98.20")
        client2.loop_start()
    elif currClient == 1:

        # OBU2 client
        client3.on_connect = on_connect3
        client3.on_message = on_message3

        client3.connect("192.168.98.30")
        client3.loop_start()
    elif currClient == 2:

        # OBU3 client
        client4.on_connect = on_connect4
        client4.on_message = on_message4

        client4.connect("192.168.98.40")
        client4.loop_start()
    elif currClient == 3:

        # OBU4 client
        client5.on_connect = on_connect5
        client5.on_message = on_message5

        client5.connect("192.168.98.50")
        client5.loop_start()
    elif currClient == 4:

        # OBU4 client
        client6.on_connect = on_connect6
        client6.on_message = on_message6

        client6.connect("192.168.98.60")
        client6.loop_start()
    elif currClient == 5:

        # OBU4 client
        client7.on_connect = on_connect7
        client7.on_message = on_message7

        client7.connect("192.168.98.70")
        client7.loop_start()
    elif currClient == 6:

        # OBU4 client
        client8.on_connect = on_connect8
        client8.on_message = on_message8

        client8.connect("192.168.98.80")
        client8.loop_start()

    # Wait
    if currClient == 1:
        time.sleep(1)
    elif currClient == 2:
        time.sleep(2)
    elif currClient == 3:
        time.sleep(3)
    if currClient == 4:
        time.sleep(4)
    elif currClient == 5:
        time.sleep(5)
    elif currClient == 6:
        time.sleep(6)

    repeatDenm = False
    interval = 0
    curr_distance = 0
    msgNum = 0
    simulatorClient.connect("127.0.0.1", port=1883)
    simulatorClient.loop_start()

    lat = startPoint[0]
    lng = startPoint[1]

    velocity = vals["speed"]
    checkTime = vals["checkTime"]

    msg_payload = "{\"accEngaged\":true,\"acceleration\":0,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":90,\"headingConf\":127,\"latitude\":" + \
        str(lat) + ",\"length\":100,\"longitude\":" + \
        str(lng) + ",\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":" + \
        str(velocity) + ",\"speedConf\":127,\"speedLimiter\":true,\"stationID\":" + \
        str(currClient) + ",\"stationType\":" + \
        str(stationType) + ",\"width\":30,\"yawRate\":0}"
    # print("OBU" + str(currClient) + ", vel: " +
    #      str(velocity) + ", time: " + str(checkTime))
    msgNum += 1
    clientsList[currClient].publish(
        topic="vanetza/in/cam", payload=msg_payload)
    simulatorClient.publish(topic="cams", payload=msg_payload)

    time.sleep(0.1)

    while True:

        print("OBU" + str(currClient) + "GroupID: " + str(vals["groupID"]))

        #print("OBU: " + str(currClient), end="\r")
        # print("\n")

        if repeatDenm:
            print("Repeating denm: " + str(currClient))
            denm_payload = "{\
                    \"management\": { \
                        \"actionID\": {\
                            \"originatingStationID\":" + str(currClient)+",\
                            \"sequenceNumber\": 0\
                        },\
                        \"detectionTime\": 1626453837.658,\
                        \"referenceTime\": 1626453837.658,\
                        \"eventPosition\": {\
                            \"latitude\":" + str(lat*const) + ",\
                            \"longitude\": " + str(lng*const) + ",\
                            \"positionConfidenceEllipse\": {\
                                \"semiMajorConfidence\": 0,\
                                \"semiMinorConfidence\": 0,\
                                \"semiMajorOrientation\": 0\
                            },\
                            \"altitude\": {\
                                \"altitudeValue\": 0,\
                                \"altitudeConfidence\": 1\
                            }\
                        },\
                        \"validityDuration\": 0,\
                        \"stationType\": " + str(stationType)+"\
                    },\
                    \"situation\": {\
                        \"informationQuality\": 7,\
                        \"eventType\": {\
                            \"causeCode\": 100,\
                            \"subCauseCode\": 14\
                        }\
                    }\
                }"
            clientsList[currClient].publish(
                topic="vanetza/in/denm", payload=denm_payload)

        if msgNum == checkTime:
            msgNum = 0
            # if currentLeader.value != currClient:
            leader = leaderCheck(currClient, mySurr, currentGroup)
            if leader:
                currentGroup = currClient
                simulatorClient.publish(
                    topic="leaders", payload="{\"leader\":" + str(currClient) + ",\"stationType\":" + str(stationType) + "}")
                denm_payload = "{\
                    \"management\": { \
                        \"actionID\": {\
                            \"originatingStationID\":" + str(currClient)+",\
                            \"sequenceNumber\": 0\
                        },\
                        \"detectionTime\": 1626453837.658,\
                        \"referenceTime\": 1626453837.658,\
                        \"eventPosition\": {\
                            \"latitude\":" + str(lat*const) + ",\
                            \"longitude\": " + str(lng*const) + ",\
                            \"positionConfidenceEllipse\": {\
                                \"semiMajorConfidence\": 0,\
                                \"semiMinorConfidence\": 0,\
                                \"semiMajorOrientation\": 0\
                            },\
                            \"altitude\": {\
                                \"altitudeValue\": 0,\
                                \"altitudeConfidence\": 1\
                            }\
                        },\
                        \"validityDuration\": 0,\
                        \"stationType\": " + str(stationType)+"\
                    },\
                    \"situation\": {\
                        \"informationQuality\": 7,\
                        \"eventType\": {\
                            \"causeCode\": 100,\
                            \"subCauseCode\": 14\
                        }\
                    }\
                }"

                vals["speed"] = sync_stats["100"][0]
                vals["checkTime"] = sync_stats["100"][2]
                checkTime = sync_stats["100"][2]
                clientsList[currClient].publish(
                    topic="vanetza/in/denm", payload=denm_payload)
                print("I'm the leader: " + str(currClient))
                repeatDenm = True
        else:
            # Next position calculation
            velocity = vals["speed"]
            checkTime = vals["checkTime"]
            distance_mt = velocity * 0.1
            curr_distance += distance_mt
            end_point = geopy.distance.geodesic(
                meters=distance_mt).destination((lat, lng), bearings[interval])

            lat = end_point.latitude
            lng = end_point.longitude

            msg_payload = "{\"accEngaged\":true,\"acceleration\":0,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":90,\"headingConf\":127,\"latitude\":" + \
                str(lat*const) + ",\"length\":100,\"longitude\":" + \
                str(lng*const) + ",\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":" + \
                str(velocity) + ",\"speedConf\":127,\"speedLimiter\":true,\"stationID\":" + \
                str(currClient) + ",\"stationType\":" + \
                str(stationType) + ",\"width\":30,\"yawRate\":0}"
            # print("OBU" + str(currClient) + ", vel: " +
            #      str(velocity) + ", time: " + str(checkTime))
            msgNum += 1
            clientsList[currClient].publish(
                topic="vanetza/in/cam", payload=msg_payload)
            simulatorClient.publish(topic="cams", payload=msg_payload)

            if curr_distance >= distances[interval]:
                interval += 1
                curr_distance = 0
                if interval == len(bearings):
                    break

            time.sleep(0.1)


def get_bearing(lat1, lat2, long1, long2):
    """
    brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['WGS84']
    print(brng)
    """
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth, back_azimuth, distance = geodesic.inv(
        long1, lat1, long2, lat2)
    return fwd_azimuth


def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):

    loc = "{},{};{},{}".format(
        pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc)
    if r.status_code != 200:
        return {}

    res = r.json()
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location']
                   [1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location']
                 [1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']

    out = {'route': routes,
           'start_point': start_point,
           'end_point': end_point,
           'distance': distance
           }

    return out


def main():

    print(r""" ____  _                 _       _             
/ ___|(_)_ __ ___  _   _| | __ _| |_ ___  _ __ 
\___ \| | '_ ` _ \| | | | |/ _` | __/ _ \| '__|
 ___) | | | | | | | |_| | | (_| | || (_) | |   
|____/|_|_| |_| |_|\__,_|_|\__,_|\__\___/|_|   
                                               """)
    """
    pickup_lon, pickup_lat, dropoff_lon, dropoff_lat = - \
        95.98588, 42.48252, -95.24417, 42.47494
    test_route = get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    """

    # get path
    gpxFile = "route2.gpx"
    coordsList = parseGPX(gpxFile)
    #coordsList = test_route['route']
    print(coordsList)
    distances = []
    bearings = []
    for i in range(0, int((len(coordsList)-1))):
        if coordsList[i] != coordsList[i+1]:
            distances.append(geopy.distance.geodesic(
                coordsList[i], coordsList[i+1]).m)
            bearings.append(get_bearing(
                coordsList[i][0], coordsList[i+1][0], coordsList[i][1], coordsList[i+1][1]))

    start_point = coordsList[0]
    pList = []
    #currentLeader = multiprocessing.Value('i', -1)
    currentGroup = -1

    for i in range(0, 4):
        # OBU Process
        p = multiprocessing.Process(
            target=startSimul, args=(i, start_point, distances, bearings, 7, surroudingsList[i], currentGroup, valsList[i], sync_stats))
        p.start()
        pList.append(p)

    for process in pList:
        process.join()
        print("Process " + str(process.pid) + " has ended")

    # both processes finished
    print("Done!")

    client2.disconnect
    client3.disconnect
    client4.disconnect
    client5.disconnect
    simulatorClient.disconnect


if __name__ == "__main__":
    main()
