import requests
from dotenv import load_dotenv
load_dotenv()
from os import getenv

#class that contains objects Point with latitude, longitude and adress as attributes
class Point:
    def __init__(self, lat=None, long=None, address=None):
        if address is None:
            self.lat = lat
            self.long = long
            #self.address = self.get_adr_from_cor()
        else:
            self.address = address
            self.lat, self.long = self.get_cor_from_adr()

    def __eq__(self, other):
        return (self.lat == other.lat) and (self.long == other.long)

    def to_LatLong(self):
        return str(self.lat)+','+str(self.long)

    def to_LongLat(self):
        return str(self.long)+','+str(self.lat)

    def get_adr_from_cor(self):
        api_key = getenv("LOCATION_IQ_KEY")
        latitude = self.lat
        longitude = self.long
        data = dict(key=api_key, lat=str(latitude), lon=str(longitude), format='json')

        reponse = requests.get("https://us1.locationiq.com/v1/reverse.php", params=data)
        resp = reponse.json()
        return resp['display_name']

    def get_cor_from_adr(self):
        api_key = getenv("LOCATION_IQ_KEY")
        data = dict(key=api_key, q=self.address, format='json')
        reponse = requests.get("https://us1.locationiq.com/v1/search.php", params=data)
        resp = reponse.json()
        return (resp[0]['lat'], resp[0]['lon'])

if __name__ == "__main__":
    PointA = Point(48.693259, 2.155216)
    print(PointA.get_adr_from_cor())
    print(Point(address='Tour Eiffel'))

    ### TO DO : definir un point à partir d'une addresse