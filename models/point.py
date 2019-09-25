import requests
from dotenv import load_dotenv
import os
load_dotenv()

class Point:
    def __init__(self, lat, long):
        self.lat=lat
        self.long=long
        #self.address = API(lat, long)

    def get_adr_from_cor(self):
        api_key = os.getenv("LOCATION_IQ_KEY")
        latitude = self.lat
        longitude = self.long
        data = dict(key= api_key, lat=str(latitude), lon=str(longitude), format='json')

        reponse = requests.get("https://us1.locationiq.com/v1/reverse.php",params = data)
        resp = reponse.json()
        return resp['display_name']

def get_cor_from_adr(adresse):
    api_key = os.getenv("LOCATION_IQ_KEY")
    data = dict(key=api_key, q = adresse, format='json')
    reponse = requests.get("https://us1.locationiq.com/v1/search.php", params=data)
    resp = reponse.json()
    return (resp[0]['lat'],resp[0]['lon'])




PointA = Point(48.693259,2.155216)
print(PointA.get_adr_from_cor())
print(get_cor_from_adr('Tour Eiffel'))




    ### TO DO : definir un point à partir d'une addresse