from dotenv import load_dotenv
import os
load_dotenv()

import models.point
from lib.openrouteservice import *
from lib.bird import *
from lib.velib import *
from lib.gmaps_to_geojson import *


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
        self.cost_per_km=10 #Très conservatif en cas de manque d'information
        self.fixed_cost=5 #Très conservatif en cas de manque d'information
        self.C02_per_km=0 #Si on n'a pas d'information on va partir du principe que la production de C02 est faible (transport en commun, etc...)
        self.calories_per_hour=0 #Si on a pas d'information on va partir du principe que cela n'est pas une activité sportive
        self.rain_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter en cas de pluie
        self.disability_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter si en situation de PMR
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

    def budget(self):
        self.total_cost = float(self.fixed_cost) + float(self.distance)*float(self.cost_per_km)
        pass

    def carbon_emission(self):
        self.total_C02= float(self.distance)*float(self.C02_per_km)
        pass

    def calories(self):
        self.total_calories= float(self.calories_per_hour)*float(self.duration)/3600
        pass

    def rain_compatible(self):
        pass

    def disability_compatible(self):
        pass

###ITINERAIRES DIRECTS : pas besoin de transiter par une station
class DirectItineray(Itinerary):
    def __init__(self, start, end):
        super().__init__(self, start, end)

    def __str__(self):
        return "L'itinéraire {} mesure {}m et dure {}s.".format(self.itinerary_name,self.distance, self.duration)


class FootItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "foot-walking")
        self.itinerary_name="à pied"


class BikeItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-regular")
        ##Green color for the geojson
        self.geojson["properties"]["color"]="#026928"
        self.itinerary_name = "en vélo"

class ElectricBikeItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-electric")
        ##Red color for the geojson
        self.geojson["properties"]["color"]="#AA0115"
        self.itinerary_name = "en vélo éléctrique"

class CarItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "driving-car")
        self.itinerary_name = "en voiture"


class TransitItinerary(DirectItineray):
    def __init__(self, start, end):
        (self.duration, self.distance, self.geojson) = gmaps_transit_itinerary(start, end)
        self.itinerary_name = "en transports en commun"


###ITINERAIRES INDIRECTS : passe par des stations (vélib, autolib, Lime....)
class IndirectItinerary(Itinerary):
    ##Fonction qui relie des points avec des stations
    def __init__(self , start, end):
        self.distance = sum([route.distance for route in self.routes])
        self.duration = sum([route.duration for route in self.routes])
        self.geojson = [route.geojson for route in self.routes]

class VelibItinerary(IndirectItinerary):
    def GiveStations(self, start, end):
        latA, longA = closest_velib_station(start.lat, start.long)
        latB, longB = closest_velib_station(end.lat, end.long)
        return models.Point(latA, longA), models.Point(latB, longB)

    def __init__(self, start, end):
        (stationA, stationB) = self.GiveStations(start, end)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start,stationA), fact.generate_route("bike",stationA, stationB), FootItinerary(stationB,end)]
        super().__init__(start, end)
        self.cost = velib_cost(self.duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff

class BirdItinerary(IndirectItinerary):
    def FindScooter(self, start):
        scooter_lat, scooter_long = bird_find_scooter(start.lat, start.long)
        return models.Point(scooter_lat, scooter_long)

    def __init__(self, start, end):
        scooter = self.FindScooter(start)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start,scooter), fact.generate_route("electric_bike", scooter, end)]
        ## to do : change speed (scooter is slower than a bike)
        super().__init__(start, end)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff