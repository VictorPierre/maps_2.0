from dotenv import load_dotenv
import os
load_dotenv()
import requests
import googlemaps
import models.point
from lib.openrouteservice import *
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
        means_of_transport="foot-walking"
        (self.duration,self.distance)= openrouteservice_itinerary(start, end, means_of_transport)

    def __str__(self):
        return "L'itinéraire piéton mesure {}m et dure {}s".format(self.distance,self.duration)


class BikeItinerary(DirectItineray):
    def __init__(self, start, end):
        means_of_transport="cycling-regular"
        (self.duration,self.distance)= openrouteservice_itinerary(start, end, means_of_transport)

    def __str__(self):
        return "L'itinéraire en vélo mesure {}m et dure {}s".format(self.distance,self.duration)


class ElectricBikeItinerary(DirectItineray):
    def __init__(self, start, end):
        means_of_transport="cycling-electric"
        (self.duration,self.distance)= openrouteservice_itinerary(start, end, means_of_transport)

    def __str__(self):
        return "L'itinéraire en vélo élétrique mesure {}m et dure {}s".format(self.distance,self.duration)


class CarItinerary(DirectItineray):
    def __init__(self, start, end):
        means_of_transport="driving-car"
        (self.duration,self.distance)= openrouteservice_itinerary(start, end, means_of_transport)

    def __str__(self):
        return "L'itinéraire en voiture mesure {}m et dure {}s".format(self.distance,self.duration)





class TransitItinerary(DirectItineray):
    def __init__(self, start, end):
        gmaps = googlemaps.Client(key=googlemaps_api_key)
        # Request directions via public transit (GoogleMaps)
        directions_result = gmaps.directions(start.to_LatLong(), end.to_LatLong(), mode="transit")
        self.duration = directions_result[0]['legs'][0]['duration']['value']
        self.distance = directions_result[0]['legs'][0]['distance']['value']

    def __str__(self):
        return "L'itinéraire en transports mesure {}m et dure {}s".format(self.distance,self.duration)



###ITINERAIRES INDIRECTS : passe par des stations (vélib, autolib, Lime....)
class IndirectItinerary(Itinerary):
    ##Fonction qui relie des points avec des stations

    def route(self,start, end, stationA, stationB):
        pass
    pass

class VelibItinerary(IndirectItinerary):

    def Station_plus_proche(depart) :
        reponse = requests.get('https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&exclude.nbbike=0&geofilter.distance=' + str(depart.lat)+'%2C+' + str(depart.long) +'%2C+1000')
        resp = reponse.json()
        lat = resp['records'][0]['fields']['geo'][0]
        long = resp['records'][0]['fields']['geo'][1]
        Station = models.Point(lat, long)
        return Station

    def GiveStations(self, start, end):
        stationA = VelibItinerary.Station_plus_proche(start)
        stationB = VelibItinerary.Station_plus_proche(end)
        return stationA, stationB

    def __init__(self, start, end):
        (stationA, stationB) = self.GiveStations(start, end)
        self.routeA = FootItinerary(start,stationA)
        self.routeB = BikeItinerary(stationA, stationB)
        self.routeC = FootItinerary(stationB,end)
        self.duration = self.routeA.duration + self.routeB.duration + self.routeC.duration

    def __str__(self):
        Aff = "Première étape:" + str(self.routeA)
        Aff += "\nDeuxième étape :" + str(self.routeB)
        Aff += "\nTroisième étape:" + str(self.routeC)
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff

