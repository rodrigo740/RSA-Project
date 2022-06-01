import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mqtt import FastMQTT, MQTTConfig
from influxdb import InfluxDBClient
from datetime import datetime
import json

app = FastAPI()

host = "127.0.0.1"
port = "1883"

mqtt_config = MQTTConfig(host=host, port=port)

mqtt = FastMQTT(
    config=mqtt_config
)

mqtt.init_app(app)

# Setup database
influxClient = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
influxClient.create_database('mydb')
influxClient.get_list_database()
influxClient.switch_database('mydb')

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# mqtt methods

@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("leaders")
    mqtt.client.subscribe("cams")
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    #print("Received message: ", topic, payload.decode(), qos, properties)
    payload = json.loads(payload.decode())

    if topic == "cams":
        stationID = "obu" + str(payload["stationID"])
        # Setup Payload
        json_payload = []
        data = {
            "measurement": "cams",
            "tags": {
                "station": stationID
            },
            "time": datetime.now(),
            "fields": {
                'latitude': str(payload["latitude"]),
                'longitude': str(payload["longitude"]),
                'id': str(payload["stationID"])
            }
        }
        json_payload.append(data)

        # Send our payload
        influxClient.write_points(json_payload)

        #print(influxClient.query('select * from cams'))
    elif topic == "leaders":

        stationID = "obu" + str(payload["leader"])
        # Setup Payload
        json_payload = []
        data = {
            "measurement": "leaders",
            "tags": {
                "station": stationID
            },
            "time": datetime.now(),
            "fields": {
                'id': str(payload["leader"]),
                'stationType': str(payload["stationType"])
            }
        }
        json_payload.append(data)

        # Send our payload
        influxClient.write_points(json_payload)
        #print(influxClient.query('select * from leaders'))


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Hello World!"}


@app.get("/getLeaders")
async def getLeaders() -> dict:
    data = list(influxClient.query(
        'select LAST(id), stationType from leaders').get_points(measurement='leaders'))
    # print(data)
    return data[0]


@app.get("/getLocations")
async def getLocations() -> dict:

    data = list(influxClient.query(
        'select LAST(id), latitude, longitude from cams where id = \'0\'').get_points(measurement='cams'))
    data += list(influxClient.query(
        'select LAST(id), latitude, longitude from cams where id = \'1\'').get_points(measurement='cams'))
    data += list(influxClient.query(
        'select LAST(id), latitude, longitude from cams where id = \'2\'').get_points(measurement='cams'))
    data += list(influxClient.query(
        'select LAST(id), latitude, longitude from cams where id = \'3\'').get_points(measurement='cams'))

    leader = list(influxClient.query(
        'select LAST(id) from leaders').get_points(measurement='leaders'))[0]["last"]
    # print(data)
    dict = {}
    for item in data:
        if leader == item["last"]:
            dict["obu" + str(item["last"])
                 ] = {"lat": item["latitude"], "lng": item["longitude"], "id": item["last"], "leader": "1"}
        else:
            dict["obu" + str(item["last"])
                 ] = {"lat": item["latitude"], "lng": item["longitude"], "id": item["last"], "leader": "0"}

    # print(dict)
    return dict
