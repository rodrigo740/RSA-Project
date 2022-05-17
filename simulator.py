from anyio import Any
import paho.mqtt.client as mqtt
import signal
import gpxpy
import gpxpy.gpx
import time
import multiprocessing
import json
import math

const = pow(10, 7)

mySurroudings1 = {"1": [], "2": [], "3": []}
#mySurroudings1 = []
mySurroudings2 = {"2": (), "3": ()}
mySurroudings3 = {"2": (), "3": ()}


client1 = mqtt.Client(userdata=mySurroudings1)
client2 = mqtt.Client(userdata=mySurroudings2)
client3 = mqtt.Client(userdata=mySurroudings3)
clientsList = [client1, client2, client3]


def handler(signum, frame):
    print("\nDisconnecting Mqtt client")
    client1.disconnect
    client2.disconnect
    client3.disconnect
    exit(1)


signal.signal(signal.SIGINT, handler)

# The callback for when the client receives a CONNACK response from the server.


def on_connect1(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        client1.subscribe("vanetza/out/cam")


# The callback for when a PUBLISH message is received from the server.
def on_message1(client, userdata, msg):
    #print("RSU got: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"])
    userdata[str(payload["stationID"])].append(pos)
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
    #print("OBU 1: ")
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

    #msg_payload = "{\"accEngaged\":true,\"acceleration\":0,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":3601,\"headingConf\":127,\"latitude\":400000000,\"length\":100,\"longitude\":-80000000,\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":16383,\"speedConf\":127,\"speedLimiter\":true,\"stationID\":1,\"stationType\":15,\"width\":30,\"yawRate\":0}"

    #client.publish(topic="vanetza/in/cam", payload=msg_payload)


# The callback for when a PUBLISH message is received from the server.
def on_message3(client, userdata, msg):
    #print("OBU 2: ")
    payload = json.loads(msg.payload)
    pos = (payload["latitude"], payload["longitude"], payload["heading"])
    userdata[str(payload["stationID"])] = pos
    # print(userdata)
    # print(payload)


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


def leaderCheck(currClient):

    # heading
    # north - 0
    # east - 90
    # west - -90
    # south 180/-180

    currInfo = None
    myInfo = ()
    otherInfo = ()

    if currClient == 1:
        # OBU1 client
        myInfo = mySurroudings2["2"]
        otherInfo = mySurroudings2["3"]

    elif currClient == 2:
        myInfo = mySurroudings3["3"]
        otherInfo = mySurroudings3["2"]

    if otherInfo != () and myInfo != ():
        # print(myInfo)
        # print(otherInfo)
        bearingToOtherCar = calcBearing(
            lat1=myInfo[0]/const, lon1=myInfo[1]/const, lat2=otherInfo[0]/const, lon2=otherInfo[1]/const)
        bearingOfThisCar = myInfo[2]
        relativeBearing = bearingToOtherCar - bearingOfThisCar
        if (relativeBearing < -180):
            relativeBearing = 360 + relativeBearing
        if (relativeBearing > 180):
            relativeBearing = 360 - relativeBearing

        print("My Bearing: " + str(relativeBearing))

        if relativeBearing <= -50 or relativeBearing <= 50:
            print("I'm behind: " + str(currClient))
        elif relativeBearing >= 130 or relativeBearing <= 230:
            print("I'm in front: " + str(currClient))


def startSimul(currClient, coordsList):
    print("Client: " + str(currClient) + " has started the simulation")

    # Connecting to the broker
    if currClient == 0:
        # RSU client
        client1.on_connect = on_connect1
        client1.on_message = on_message1

        client1.connect("192.168.98.10")
        client1.loop_start()
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

    # Wait 5 seconds
    if currClient > 1:
        time.sleep(2)

    if currClient != 0:
        myID = int(currClient) + 1

        for coords in coordsList:
            lat = coords[0]*const
            lng = coords[1]*const
            msg_payload = "{\"accEngaged\":true,\"acceleration\":0,\"altitude\":800001,\"altitudeConf\":15,\"brakePedal\":true,\"collisionWarning\":true,\"cruiseControl\":true,\"curvature\":1023,\"driveDirection\":\"FORWARD\",\"emergencyBrake\":true,\"gasPedal\":false,\"heading\":270,\"headingConf\":127,\"latitude\":" + \
                str(lat) + ",\"length\":100,\"longitude\":" + \
                str(lng) + ",\"semiMajorConf\":4095,\"semiMajorOrient\":3601,\"semiMinorConf\":4095,\"specialVehicle\":{\"publicTransportContainer\":{\"embarkationStatus\":false}},\"speed\":16383,\"speedConf\":127,\"speedLimiter\":true,\"stationID\":" + \
                str(myID) + ",\"stationType\":15,\"width\":30,\"yawRate\":0}"

            clientsList[currClient].publish(
                topic="vanetza/in/cam", payload=msg_payload)
            time.sleep(0.1)
            leaderCheck(currClient)

    while(True):
        pass
    """
    if currClient == 0:
        # RSU client
        # client1.loop_forever()
        print("Client 0 heading out")
    elif currClient == 1:
        # OBU1 client
        # client2.loop()
        print("Client 1 heading out")
    elif currClient == 2:
        # OBU2 client
        client1.disconnect()
        client2.disconnect()
        client3.disconnect()
    """


def main():
    # setupMqtt()
    gpxFile = "route-1.gpx"
    coordsList = parseGPX(gpxFile)

    pList = []

    # RSU Process
    p1 = multiprocessing.Process(target=startSimul, args=(0, coordsList))
    p1.start()
    pList.append(p1)

    for i in range(1, len(clientsList)):
        # OBU Process
        p = multiprocessing.Process(target=startSimul, args=(i, coordsList))
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


if __name__ == "__main__":
    main()
