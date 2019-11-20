from dotenv import load_dotenv
load_dotenv()
from os import getenv

import requests
from math import ceil

from .exceptions import *


def find_scooter(lat,long):
    """
    function which gives the location of the closest bird scooter
    :param lat:
    :param long:
    :return (lat, long): tuple of string
    """

    url = "https://api.birdapp.com/bird/nearby"
    params = {"latitude": lat, "longitude": long, "radius": "1000"}
    headers = {
        'Authorization': getenv("BIRD_KEY"),
        'Device-id': "123E4567-E89B-12D3-A456-426655440780",
        'App-Version': "4.41.0",
        'Location': "{\"latitude\":"+str(lat)+",\"longitude\":"+str(long)+",\"altitude\":500,\"accuracy\":100,\"speed\":-1,\"heading\":-1}",
        'cache-control': "no-cache",
    }
    response = requests.get(url, headers=headers, params=params)
    resp = response.json()

    if response.status_code != 200:
        raise ApiException('API Bird ne répond pas')
    if len(resp['birds']) == 0 :
        raise ValueError('Pas de bird trouvé dans la zone')
    scooter_location = resp['birds'][0]["location"]
    return(scooter_location['latitude'],scooter_location['longitude'])

def cost(duration):
    """
    retourne le coût en euros pour une durée de trajet en minute
    :param duration: integer, in minutes
    :return cost: integer, in euros
    """
    return 1 + 0.25*ceil(duration/60)

#print(bird_find_scooter(48.83278,2.33800))
#to do : recuperer la trotinette optimale et pas la plus proche
#estimation du prix
# estimation vitesse : 15km/h