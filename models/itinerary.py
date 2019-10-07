from dotenv import load_dotenv
import os
load_dotenv()

import models.point
from lib.openrouteservice import *
from lib.bird import *
from lib.velib import *
import googlemaps

class ItineraryFactory:
    def generate_route(self, type, start, end):
        generator = ItineraryFactory.get_generator(type)
        return generator(start, end)

    @classmethod
    def available_types(cls):
        return [("foot", "marche"),
                ("bike", "vélo"),
                ("electric_bike", "vélo électrique"),
                ("velib", "Vélib"),
                ("transit", "transports en commun"),
                ("car", "voiture"),
                ("bird", "Bird")
                ]

    @classmethod
    def get_generator(cls, type):
        if type == 'foot':
            return FootItinerary
        elif type == 'bike':
            return BikeItinerary
        elif type == 'electric_bike':
            return ElectricBikeItinerary
        elif type == 'velib':
            return VelibItinerary
        elif type == 'transit':
            return TransitItinerary
        elif type == 'car':
            return CarItinerary
        elif type == 'bird':
            return BirdItinerary
        else:
            raise ValueError('Moyen de transport inconnu : '+type)


class Itinerary:
    def __init__(self, start, end):
        pass

    def route(start, end):
        ##return a distance, duration and geoJSON
        pass

    def to_json(self):
        json = {
            "duration": self.duration,
            "distance": self.distance,
            "html": self.__str__(),
        }
        if hasattr(self, 'geojson'):
            json["geojson"]= self.geojson

        return json
###ITINERAIRES DIRECTS : pas besoin de transiter par une station
class DirectItineray(Itinerary):
    pass


class FootItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "foot-walking")

    def __str__(self):
        return "L'itinéraire piéton mesure {}m et dure {}s.".format(self.distance,self.duration)


class BikeItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-regular")

    def __str__(self):
        return "L'itinéraire en vélo mesure {}m et dure {}s".format(self.distance,self.duration)


class ElectricBikeItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-electric")

    def __str__(self):
        return "L'itinéraire en vélo élétrique mesure {}m et dure {}s".format(self.distance,self.duration)


class CarItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "driving-car")

    def __str__(self):
        return "L'itinéraire en voiture mesure {}m et dure {}s".format(self.distance,self.duration)

class TransitItinerary(DirectItineray):
    def __init__(self, start, end):
        gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        # Request directions via public transit (GoogleMaps)
        directions_result = gmaps.directions(start.to_LatLong(), end.to_LatLong(), mode="transit")
        self.duration = directions_result[0]['legs'][0]['duration']['value']
        self.distance = directions_result[0]['legs'][0]['distance']['value']

    def __str__(self):
        return "L'itinéraire en transports mesure {}m et dure {}s".format(self.distance,self.duration)

###ITINERAIRES INDIRECTS : passe par des stations (vélib, autolib, Lime....)
class IndirectItinerary(Itinerary):
    ##Fonction qui relie des points avec des stations
    def __init__(self , start, end, type):
        (stationA, stationB) = self.GiveStations(start, end)
        fact = ItineraryFactory()
        self.routeA = FootItinerary(start,stationA)
        self.routeB = fact.generate_route(type,stationA, stationB)
        self.routeC = FootItinerary(stationB,end)
        self.distance = self.routeA.distance + self.routeB.distance + self.routeC.distance
        self.duration = self.routeA.duration + self.routeB.duration + self.routeC.duration

class VelibItinerary(IndirectItinerary):
    def GiveStations(self, start, end):
        latA, longA = closest_velib_station(start.lat, start.long)
        latB, longB = closest_velib_station(end.lat, end.long)
        return models.Point(latA, longA), models.Point(latB, longB)

    def __init__(self, start, end):
        super().__init__(start, end, "bike")
        self.cost = velib_cost(self.duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routeA)
        Aff += "\nDeuxième étape :" + str(self.routeB)
        Aff += "\nTroisième étape:" + str(self.routeC)
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff

class BirdItinerary(IndirectItinerary):
    def GiveStations(self, start, end):
        scooter_lat, scooter_long = bird_find_scooter(start.lat, start.long)
        return models.Point(scooter_lat, scooter_long), end

    def __init__(self, start, end):
        ## to do : change speed (scooter is slower than a bike)
        super().__init__(start, end, "bike")

    def __str__(self):
        Aff = "Première étape:" + str(self.routeA)
        Aff += "\nDeuxième étape :" + str(self.routeB)
        Aff += "\nTroisième étape:" + str(self.routeC)
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff
