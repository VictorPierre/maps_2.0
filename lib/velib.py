import requests

def closest_velib_station(lat,long):
    reponse = requests.get(
        'https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&exclude.nbbike=0&geofilter.distance=' + str(
            lat) + '%2C+' + str(long) + '%2C+1000')
    resp = reponse.json()
    station_lat = resp['records'][0]['fields']['geo'][0]
    station_long = resp['records'][0]['fields']['geo'][1]
    return station_lat, station_long