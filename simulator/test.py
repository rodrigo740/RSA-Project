import requests
import polyline
import gpxpy
import gpxpy.gpx
import folium


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


def get_map(route):

    m = folium.Map(location=[(route['start_point'][0] + route['end_point'][0])/2,
                             (route['start_point'][1] + route['end_point'][1])/2],
                   zoom_start=13)

    folium.PolyLine(
        route['route'],
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(m)

    folium.Marker(
        location=route['start_point'],
        icon=folium.Icon(icon='play', color='green')
    ).add_to(m)

    folium.Marker(
        location=route['end_point'],
        icon=folium.Icon(icon='stop', color='red')
    ).add_to(m)

    return m


# get path
gpxFile = "route2.gpx"
coordsList = parseGPX(gpxFile)
pickup_lon, pickup_lat, dropoff_lon, dropoff_lat = - \
    95.98588, 42.48252, -95.24417, 42.47494
test_route = get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
get_map(test_route)
print(test_route)
for i in test_route['route']:
    print(i)
print("Len gpx: " + str(len(coordsList)))
print("Len request: " + str(len(test_route['route'])))
