import requests
from lib.API_Exception import *

def closest_velib_station(lat,long):

    reponse = requests.get(
        'https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&exclude.nbbike=0&geofilter.distance=' + str(
            lat) + '%2C+' + str(long) + '%2C+1000')
    if reponse.status_code != 200 :
        raise ApiException ('API Vélib ne répond pas')
    resp = reponse.json()
    if resp['nhits'] == 0:
        raise ValueError("Pas de station Velib dans la zone")
    station_lat = resp['records'][0]['fields']['geo'][0]
    station_long = resp['records'][0]['fields']['geo'][1]
    return station_lat, station_long


