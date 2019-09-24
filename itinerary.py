from dotenv import load_dotenv
import os
load_dotenv()
import requests

class Itinerary:
    def __init__(self, start, end):
        pass

    @classmethod
    def route(start, end):
        ##return a distance, duration and geoJSON
        pass

###ITINERAIRES DIRECTS : pas besoin de transiter par une station
class DirectItineray(Itinerary):
    pass

class FootItinerary(DirectItineray):
    def __init__(self, start, end):
        api_key = os.getenv("OPEN_ROUTE_SERVICE_API_KEY")
        start = str(start.lat) + ',' + str(start.long)
        end = str(end.lat) + ',' + str(end.long)
        params = {'api_key': api_key, 'start': start, 'end': end}
        reponse = requests.get("https://api.openrouteservice.org/v2/directions/foot-walking", params=params)
        resp = reponse.json()
        self.duration = resp['features'][0]["properties"]['segments'][0]['duration']
        self.distance = resp['features'][0]["properties"]['segments'][0]['distance']

class TransitItinerary(DirectItineray):
    pass

class BikeItinerary(DirectItineray):
    pass


###ITINERAIRES INDIRECTS : passe par des stations (vélib, autolib, Lime....)
class IndirectItinerary(Itinerary):
    ##Fonction qui relie des points avec des stations
    def route(self,start, end, stationA, stationB):
        pass
    pass

class VelibItinerary(IndirectItinerary):
    def GiveStations(self, start, end):
        return stationA, stationB