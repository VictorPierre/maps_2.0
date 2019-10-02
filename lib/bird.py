from dotenv import load_dotenv
import os
load_dotenv()
import requests
from math import ceil

def bird_find_scooter(lat,long):
    url = "https://api.birdapp.com/bird/nearby"
    params = {"latitude": lat, "longitude": long, "radius": "1000"}
    headers = {
        'Authorization': os.getenv("BIRD_KEY"),
        'Device-id': "123E4567-E89B-12D3-A456-426655440780",
        'App-Version': "4.41.0",
        'Location': "{\"latitude\":"+str(lat)+",\"longitude\":"+str(long)+",\"altitude\":500,\"accuracy\":100,\"speed\":-1,\"heading\":-1}",
        'cache-control': "no-cache",
    }
    response = requests.get(url, headers=headers, params=params)
    resp = response.json()
    scooter_location = resp['birds'][0]["location"]
    return(scooter_location['latitude'],scooter_location['longitude'])

#retourne le coût en euros pour une durée de trajet en minute
def bird_cost(duration):
    return 1 + 0.25*ceil(duration)

#print(bird_find_scooter(48.83278,2.33800))
#to do : recuperer la trotinette optimale et pas la plus proche
#estimation du prix
# estimation vitesse : 15km/h