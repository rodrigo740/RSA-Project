from anyio import Any
import paho.mqtt.client as mqtt
import signal
import gpxpy
import gpxpy.gpx
import time
import multiprocessing
import json
import math
from time import sleep
const = pow(10, 7)

mySurroudings1 = {"1": [], "2": [], "3": [], "4": [], "5": []}
mySurroudings2 = {"2": (), "3": (), "4": (), "5": ()}
mySurroudings3 = {"2": (), "3": (), "4": (), "5": ()}
mySurroudings4 = {"2": (), "3": (), "4": (), "5": ()}
mySurroudings5 = {"2": (), "3": (), "4": (), "5": ()}

currentLeader = 0

client1 = mqtt.Client(userdata=mySurroudings1)
client2 = mqtt.Client(userdata=mySurroudings2)
client3 = mqtt.Client(userdata=mySurroudings3)
client4 = mqtt.Client(userdata=mySurroudings4)
client5 = mqtt.Client(userdata=mySurroudings5)
clientsList = [client1, client2, client3, client4, client5]

simulatorClient = mqtt.Client()


def handler(signum, frame):
    print("\nDisconnecting Mqtt client")
    client1.disconnect
    client2.disconnect
    client3.disconnect
    client4.disconnect
    client5.disconnect
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


def on_connect1(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client1.subscribe("vanetza/out/cam")


# The callback for when a PUBLISH message is received from the server.
def on_message1(client, userdata, msg):
    # print("RSU got: ")
    # payload = json.loads(msg.payload)
    # pos = (payload["latitude"], payload["longitude"])
    # userdata[str(payload["stationID"])].append(pos)
    simulatorClient.publish(topic="cams", payload=msg.payload)

    # print(pos)
    # Debug for loop
    # for key in userdata:
    #    print(len(userdata[key]))


# The callback for when the client receives a CONNACK response from the server.


def on_connect2(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client2.subscribe("vanetza/out/cam")
        client2.subscribe("vanetza/in/cam")

# The callback for when a PUBLISH message is received from the server.


def on_message2(client, userdata, msg):
    # print("OBU 1: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"], payload["heading"])
    userdata[str(payload["stationID"])] = pos
    # print(userdata)
    # print(payload)


# The callback for when the client receives a CONNACK response from the server.
def on_connect3(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client3.subscribe("vanetza/out/cam")
        client3.subscribe("vanetza/in/cam")

# The callback for when a PUBLISH message is received from the server.


def on_message3(client, userdata, msg):
    # print("OBU 2: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"], payload["heading"])
    userdata[str(payload["stationID"])] = pos

# The callback for when the client receives a CONNACK response from the server.


def on_connect4(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client4.subscribe("vanetza/out/cam")
        client4.subscribe("vanetza/in/cam")

# The callback for when a PUBLISH message is received from the server.


def on_message4(client, userdata, msg):
    # print("OBU 2: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"], payload["heading"])
    userdata[str(payload["stationID"])] = pos


# The callback for when the client receives a CONNACK response from the server.
def on_connect5(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client5.subscribe("vanetza/out/cam")
        client5.subscribe("vanetza/in/cam")

# The callback for when a PUBLISH message is received from the server.


def on_message5(client, userdata, msg):
    # print("OBU 2: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"], payload["heading"])
    userdata[str(payload["stationID"])] = pos


def setupMqtt():
    # RSU client
    client1.on_connect = on_connect1
    client1.on_message = on_message1

    client1.connect("192.168.98.10")
    client1.loop_start()

    # OBU1 client
    client2.on_connect = on_connect2
    client2.on_message = on_message2

    client2.connect("192.168.98.20")
    client2.loop_start()

    # OBU2 client
    client3.on_connect = on_connect3
    client3.on_message = on_message3

    client3.connect("192.168.98.30")
    client3.loop_start()


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


def interPoint(point1, point2):
    lat1 = point1[0]
    lon1 = point1[1]

    lat2 = point2[0]
    lon2 = point2[1]

    f = 0
    d = 1/10
    A = math.sin((1-f)*d)/math.sin(d)
    B = math.sin(f*d)/math.sin(d)
    x = A*math.cos(lat1)*math.cos(lon1) + B*math.cos(lat2)*math.cos(lon2)
    y = A*math.cos(lat1)*math.sin(lon1) + B*math.cos(lat2)*math.sin(lon2)
    z = A*math.sin(lat1) + B*math.sin(lat2)
    lat = math.atan2(z, math.sqrt(pow(x, 2)+pow(y, 2)))
    lon = math.atan2(y, x)

    return (lat1 + lat, lon1 + lon)


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

    #print("My Bearing: " + str(relativeBearing))

    # if relativeBearing >= -50 and relativeBearing <= 50:
    # print("I'm behind: " + str(currClient))
    #    res = False
    if relativeBearing >= 170 and relativeBearing <= 190:
        # print("I'm in front: " + str(currClient))
        res = True
    else:
        res = False

    return res


def leaderCheck(currClient):

    # heading
    # north - 0
    # east - 90
    # west - -90
    # south 180/-180

    res = False
    myInfo = ()
    otherInfo = ()
    if currClient == 1:
        # OBU1 client
        myInfo = mySurroudings2["2"]

        if currentLeader != 0:
            otherInfo = mySurroudings2[str(currentLeader+1)]
            return check(myInfo, otherInfo)
        else:
            if mySurroudings2["3"] != ():
                otherInfo = mySurroudings2["3"]
                res = check(myInfo, otherInfo)
            if mySurroudings2["4"] != ():
                otherInfo = mySurroudings2["4"]
                res = check(myInfo, otherInfo)
            if mySurroudings2["5"] != ():
                otherInfo = mySurroudings2["5"]
                res = check(myInfo, otherInfo)

    elif currClient == 2:
        myInfo = mySurroudings3["3"]

        if currentLeader != 0:
            otherInfo = mySurroudings3[str(currentLeader+1)]
            return check(myInfo, otherInfo)
        else:
            if mySurroudings3["2"] != ():
                otherInfo = mySurroudings3["2"]
                res = check(myInfo, otherInfo)
            if mySurroudings3["4"] != ():
                otherInfo = mySurroudings3["4"]
                res = check(myInfo, otherInfo)
            if mySurroudings3["5"] != ():
                otherInfo = mySurroudings3["5"]
                res = check(myInfo, otherInfo)

    elif currClient == 3:
        myInfo = mySurroudings4["4"]

        if currentLeader != 0:
            otherInfo = mySurroudings4[str(currentLeader+1)]
            return check(myInfo, otherInfo)
        else:
            if mySurroudings4["2"] != ():
                otherInfo = mySurroudings4["2"]
                res = check(myInfo, otherInfo)
            if mySurroudings4["3"] != ():
                otherInfo = mySurroudings4["3"]
                res = check(myInfo, otherInfo)
            if mySurroudings4["5"] != ():
                otherInfo = mySurroudings4["5"]
                res = check(myInfo, otherInfo)

    elif currClient == 4:
        myInfo = mySurroudings5["5"]

        if currentLeader != 0:
            otherInfo = mySurroudings5[str(currentLeader+1)]
            return check(myInfo, otherInfo)
        else:
            if mySurroudings5["2"] != ():
                otherInfo = mySurroudings5["2"]
                res = check(myInfo, otherInfo)
            if mySurroudings5["4"] != ():
                otherInfo = mySurroudings5["4"]
                res = check(myInfo, otherInfo)
            if mySurroudings5["3"] != ():
                otherInfo = mySurroudings5["3"]
                res = check(myInfo, otherInfo)

    return res


def startSimul(currClient, coordsList, stationType):
    print("Client: " + str(currClient) + " has started the simulation")
    # load reference CAM
    """
    with open('utils/in_cam.json') as f:
        refCam = json.load(f)
    """
    # Connecting to the broker
    if currClient == 0:
        # RSU client
        client1.on_connect = on_connect1
        client1.on_message = on_message1

        client1.connect("192.168.98.10")
        client1.loop_start()

        simulatorClient.on_connect = on_connectSim
        simulatorClient.on_message = on_messageSim

    elif currClient == 1:

        # OBU1 client
        client2.on_connect = on_connect2
        client2.on_message = on_message2

        client2.connect("192.168.98.20")
        client2.loop_start()
    elif currClient == 2:

        # OBU2 client
        client3.on_connect = on_connect3
        client3.on_message = on_message3

        client3.connect("192.168.98.30")
        client3.loop_start()
    elif currClient == 3:

        # OBU3 client
        client4.on_connect = on_connect4
        client4.on_message = on_message4

        client4.connect("192.168.98.40")
        client4.loop_start()
    elif currClient == 4:

        # OBU4 client
        client5.on_connect = on_connect5
        client5.on_message = on_message5

        client5.connect("192.168.98.50")
        client5.loop_start()

    # Wait 0.2 seconds
    if currClient == 2:
        time.sleep(0.2)
    elif currClient == 3:
        time.sleep(0.4)
    elif currClient == 4:
        time.sleep(0.6)

    msgNum = 0
    simulatorClient.connect("127.0.0.1", port=1883)
    simulatorClient.loop_start()

    if currClient != 0:
        myID = int(currClient) + 1
        #refCam["stationID"] = myID
        #refCam["stationType"] = stationType

        for coords in coordsList:
            lat = coords[0]*const
            lng = coords[1]*const
            #refCam["latitude"] = int(lat)
            #refCam["longitude"] = int(lng)
            """
            msg_payload = str(refCam).replace("T", "t").replace(
               "F", "f").replace("\'", "\"").replace("fORWARD", "FORWARD")

            msg_payload = str(refCam)
            """
            msg_payload = "{\"accEngaged\":true,\"acceleration\":0,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":270,\"headingConf\":127,\"latitude\":" + \
                str(lat) + ",\"length\":100,\"longitude\":" + \
                str(lng) + ",\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":16383,\"speedConf\":127,\"speedLimiter\":true,\"stationID\":" + \
                str(myID) + ",\"stationType\":" + \
                str(stationType) + ",\"width\":30,\"yawRate\":0}"
            # print(msg_payload)
            # print(type(refCam))
            msgNum += 1
            clientsList[currClient].publish(
                topic="vanetza/in/cam", payload=msg_payload)
            time.sleep(0.1)
            if msgNum == 3:
                leader = leaderCheck(currClient)
                msgNum = 0
                if leader:
                    currentLeader = currClient
                    simulatorClient.publish(
                        topic="leaders", payload="{\"leader\":" + str(currentLeader) + ",\"stationType\":" + str(stationType) + "}")
                    print("I'm the leader: " + str(currClient))
            # sleep(1)

    else:
        while(True):
            pass


def main():

    # get path
    gpxFile = "route-1.gpx"
    coordsList = parseGPX(gpxFile)
    finalCoordsList = []
    """
    for i in range(0, len(coordsList)-1):
        finalCoordsList.append(coordsList[i])
        finalCoordsList.append(interPoint(coordsList[i], coordsList[i+1]))

    print(finalCoordsList)
    """
    pList = []

    # RSU Process
    p1 = multiprocessing.Process(
        target=startSimul, args=(0, coordsList, 15))
    p1.start()
    pList.append(p1)

    for i in range(1, len(clientsList)):
        # OBU Process
        p = multiprocessing.Process(
            target=startSimul, args=(i, coordsList, 7))
        p.start()
        pList.append(p)

    for process in pList:
        process.join()
        print("Process " + str(process.pid) + " has ended")

    # both processes finished
    print("Done!")

    client1.disconnect
    client2.disconnect
    client3.disconnect
    client4.disconnect
    client5.disconnect
    simulatorClient.disconnect


if __name__ == "__main__":
    main()
