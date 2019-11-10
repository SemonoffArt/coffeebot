import requests
import json
import urllib3

from math import radians, cos, sin, asin, sqrt, ceil

def distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def getLocations(location_longitude, location_latitide, google_api_key, max_view):
    urllib3.disable_warnings()
    s = requests.Session()
    s.keep_alive = True
    face_api_url = str("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={0},{1}&type=cafe&rankby=distance&key={2}".format(location_latitide, location_longitude, google_api_key))
    response = s.get(face_api_url, verify=False).json()

    i = 1
    output = ""
    for result in response['results']:
        dist = distance(float(location_longitude), float(location_latitide), float(result['geometry']['location']['lng']), float(result['geometry']['location']['lat']))
        dist = ceil(dist * 1000)
        map_link = str("https://www.google.com/maps/search/?api=1&query=Google&query_place_id=" + str(result['place_id']))

        if "rating" in result:
            output = output + result['name'] + " ⭐️ " + str(round(result['rating'], 1)) + " ("+ str(dist) + " м.)\n"
        else:
            output = output + result['name'] + " ("+ str(dist) + " м.)\n"
        output =  output + str("[Посмотреть на карте]("+ map_link +")") + "\n"

        if i == max_view:
            break
        output =  output + str("\n")
        i = i + 1

    return output
