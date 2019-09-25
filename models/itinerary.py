from dotenv import load_dotenv
import os
load_dotenv()
import requests
import googlemaps

open_route_api_key = os.getenv("OPEN_ROUTE_SERVICE_API_KEY")
googlemaps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

class Itinerary:
    def __init__(self, start, end):
        pass

    def route(start, end):
        ##return a distance, duration and geoJSON
        pass


###ITINERAIRES DIRECTS : pas besoin de transiter par une station
class DirectItineray(Itinerary):
    pass

class FootItinerary(DirectItineray):
    def __init__(self, start, end):

        params = {'api_key': open_route_api_key, 'start': start.to_LongLat(), 'end': end.to_LongLat()}
        reponse = requests.get("https://api.openrouteservice.org/v2/directions/foot-walking", params=params)
        resp = reponse.json()
        self.duration = resp['features'][0]["properties"]['segments'][0]['duration']
        self.distance = resp['features'][0]["properties"]['segments'][0]['distance']

    def __str__(self):
        return "L'itinéraire piéton mesure {}m et dure {}s".format(self.distance,self.duration)

class TransitItinerary(DirectItineray):
    def __init__(self, start, end):
        gmaps = googlemaps.Client(key=googlemaps_api_key)
        # Request directions via public transit (GoogleMaps)
        directions_result = gmaps.directions(start.to_LatLong(), end.to_LatLong(), mode="transit")
        self.duration = directions_result[0]['legs'][0]['duration']['value']
        self.distance = directions_result[0]['legs'][0]['distance']['value']

    def __str__(self):
        return "L'itinéraire en transports mesure {}m et dure {}s".format(self.distance,self.duration)

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