import requests
from dotenv import load_dotenv
import os
load_dotenv()

import requests
from dotenv import load_dotenv
import os

load_dotenv()



class Point:
    def __init__(self, lat, long):
        self.lat=lat
        self.long=long
        #self.address = API(lat, long)

    def to_LatLong(self):
        return str(self.lat)+','+str(self.long)

    def to_LongLat(self):
        return str(self.long)+','+str(self.lat)

    def get_adr_from_cor(self):
            api_key = os.getenv("LOCATION_IQ_KEY")
            latitude = self.lat
            longitude = self.long
            data = dict(key=api_key, lat=str(latitude), lon=str(longitude), format='json')

            reponse = requests.get("https://us1.locationiq.com/v1/reverse.php", params=data)
            resp = reponse.json()
            return resp['display_name']

def get_cor_from_adr(adresse):
    api_key = os.getenv("LOCATION_IQ_KEY")
    data = dict(key=api_key, q=adresse, format='json')
    reponse = requests.get("https://us1.locationiq.com/v1/search.php", params=data)
    resp = reponse.json()
    return (resp[0]['lat'], resp[0]['lon'])

if __name__ == "__main__":
    PointA = Point(48.693259, 2.155216)
    print(PointA.get_adr_from_cor())
    print(get_cor_from_adr('Tour Eiffel'))

    ### TO DO : definir un point à partir d'une addresse