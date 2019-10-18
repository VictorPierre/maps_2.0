from dotenv import load_dotenv
import os
load_dotenv()
from flask import render_template
import numpy as np

import models.point
from lib.openrouteservice import *
from lib.bird import *
from lib.velib import *
from lib.gmaps_to_geojson import *

from threading import Thread
from multiprocessing import Queue

class ItineraryFactory:
    def __init__(self):
        self._builders = {
            "foot": FootItinerary,
            "bike": BikeItinerary,
            "electric_bike": ElectricBikeItinerary,
            "velib": VelibItinerary,
            #"transit": TransitItinerary,
            "car": CarItinerary,
            "bird": BirdItinerary,
        }

    def generate_route(self, type, start, end):
        builder = self._builders.get(type)
        if builder is None:
            raise ValueError(type)
        return builder(start, end)

    def generate_all_routes(self, start, end):
        routes = []
        for builder in self._builders:
            try :
                routes.append(self.generate_route(builder, start, end).json())
            except SameStation as e :
                print("Erreur sur un itinéraire")
                print(e)
            except ApiException as a :
                print(a)
        return routes

    def generate_route_thread(self, type, start, end, out_queue):
        builder = self._builders.get(type)
        if builder is None:
            raise ValueError(type)
        out_queue.put(builder(start, end))

    def generate_all_routes_threads_json(self, start, end):
        routes = []
        my_queue=Queue()
        for builder in self._builders:
            thread = Thread(target=self.generate_route_thread, args=(builder,start,end,my_queue,))
            thread.start()
            thread.join()
        while int(my_queue.qsize())>0 :
            routes.append(my_queue.get().json())
        return routes




class Itinerary:
    """
    ABSTRACT CLASS, implementing the following attributes/methods

    ATTRIBUTES :
    - itinerary_name (string)
    - distance (int type, distance in meters)
    - duration (int type, duration in seconds)
    - geojson (dict, data for visualising the route)
    - rain_compatible (boolean)
    - disability_compatible (boolean)

    METHODS :
    - budget(self) -> float (return the cost in €)
    - carbon_emission(self) -> float (return the CO2 emissions in kg)
    - calories(self) -> float (return the amount of kcal)
    - json(self) -> json (return a JSON containing the geojson + an HTML preview of the itinerary)
    """

    def __init__(self, start, end):
        self.cost_per_km=10 #Très conservatif en cas de manque d'information
        self.fixed_cost=5 #Très conservatif en cas de manque d'information
        self.C02_per_km=0 #Si on n'a pas d'information on va partir du principe que la production de C02 est faible (transport en commun, etc...)
        self.calories_per_hour=0 #Si on a pas d'information on va partir du principe que cela n'est pas une activité sportive
        self.rain_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter en cas de pluie
        self.disability_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter si en situation de PMR

    def budget(self):
        return float(self.fixed_cost) + float(self.distance)*float(self.cost_per_km)

    def carbon_emission(self):
        return float(self.distance)*float(self.C02_per_km)

    def calories(self):
        return float(self.calories_per_hour)*float(self.duration)/3600

    def json(self):
        return {
            "html": self.__html(),
            "geojson": self.geojson,
        }

    def __html(self):
        return render_template('show.html',
                        name=self.itinerary_name,
                        duration = self.__sec_to_time(),
                        distance = self.__meter_to_km(),
                        rain_compatible = self.rain_compatible,
                        disability_compatible = self.disability_compatible,
                        budget = self.budget(),
                        carbon_emission= self.carbon_emission(),
                        calories = self.calories(),
                        )

    #Convert self.distance into a pretty format
    def __meter_to_km(self):
        distance = int(self.distance)
        if distance < 1000 :
            return str(distance) + "m"
        else:
            return str(round(distance / 1000, 1)) + "km"

    # Convert self.duration into a pretty format
    def __sec_to_time(self):
        time = int(self.duration)
        heure = time//3600
        minute = int((time-heure*3600)//60)
        seconde = int((time - heure*3600 - minute*60))
        if heure == 0 :
            if minute == 0:
                return str(time) + "s"
            else:
                return str(minute)+"mn"
        else:
            return str(heure)+"h"+str(minute)+"mn"


###ITINERAIRES DIRECTS : pas besoin de transiter par une station

class FootItinerary(Itinerary):
    def __init__(self, start, end):
        self.itinerary_name = "à pied"
        self.calories_per_hour = 168
        self.rain_compatible = True
        self.disability_compatible = True
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "foot-walking")

    def budget(self):
        return 0
    def carbon_emission(self):
        return 0


class BikeItinerary(Itinerary):
    def __init__(self, start, end):
        self.itinerary_name = "en vélo"
        self.calories_per_hour = 300
        self.rain_compatible = False
        self.disability_compatible = False
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-regular")
        ##Green color for the geojson
        self.geojson["properties"]["color"]="#026928"

    def budget(self):
        return 0
    def carbon_emission(self):
        return 0

class ElectricBikeItinerary(Itinerary):
    def __init__(self, start, end):
        self.itinerary_name = "en vélo éléctrique"
        self.calories_per_hour = 0
        self.rain_compatible = False
        self.disability_compatible = False
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "cycling-electric")
        ##Red color for the geojson
        self.geojson["properties"]["color"]="#AA0115"
    def budget(self):
        return 0
    def carbon_emission(self):
        return 0

class CarItinerary(Itinerary):
    def __init__(self, start, end):
        self.itinerary_name = "en voiture"
        self.calories_per_hour = 0
        self.rain_compatible = True
        self.disability_compatible = True
        (self.duration,self.distance, self.geojson)= openrouteservice_itinerary(start, end, "driving-car")
        self.geojson["properties"]["color"]="#AA0115"
    def budget(self): ##TO DO
        return 0
    def carbon_emission(self): ##TO DO
        return 0


class TransitItinerary(Itinerary):
    def __init__(self, start, end):
        self.itinerary_name = "en transports en commun"
        self.calories_per_hour = 0
        self.rain_compatible = True
        self.disability_compatible = True ##TO DO
        (self.duration, self.distance, self.geojson) = gmaps_transit_itinerary(start, end)
    def budget(self): ##TO DO
        return 0
    def carbon_emission(self): ##TO DO
        return 0


###ITINERAIRES INDIRECTS : listes d'itinéraires directs
class IndirectItinerary(Itinerary):

    def __init__(self , start, end):
        self.distance = sum([route.distance for route in self.routes])
        self.duration = sum([route.duration for route in self.routes])
        self.geojson = [route.geojson for route in self.routes]
        self.disability_compatible = np.all([route.disability_compatible for route in self.routes])
        self.rain_compatible = np.all([route.rain_compatible for route in self.routes])

    def calories(self):
        return sum([route.calories() for route in self.routes])
    def budget(self):
        return sum([route.budget() for route in self.routes])
    def carbon_emission(self):
        return sum([route.carbon_emission() for route in self.routes])

class VelibItinerary(IndirectItinerary):

    def __init__(self, start, end):
        self.itinerary_name = "Vélib"
        (stationA, stationB) = self.__GiveStations(start, end)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start,stationA), fact.generate_route("bike",stationA, stationB), FootItinerary(stationB,end)]
        super().__init__(start, end)

    def budget(self):
        return velib_cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
        return Aff

    def __GiveStations(self, start, end):
        latA, longA = closest_velib_station(start.lat, start.long)
        latB, longB = closest_velib_station(end.lat, end.long)
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de Velib sont les mêmes")
        return models.Point(latA, longA), models.Point(latB, longB)


class eVelibItinerary(IndirectItinerary):

    def __init__(self, start, end):
        self.itinerary_name = "e-velib"
        (stationA, stationB) = self.__GiveStations(start, end)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start, stationA), fact.generate_route("electric_bike", stationA, stationB),
                       FootItinerary(stationB, end)]
        super().__init__(start, end)

    def budget(self):
        return evelib_cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
        return Aff

    def __GiveStations(self, start, end):
        latA, longA = closest_evelib_station(start.lat, start.long)
        latB, longB = closest_evelib_station(end.lat, end.long)
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de eVelib sont les mêmes")

        return models.Point(latA, longA), models.Point(latB, longB)

class BirdItinerary(IndirectItinerary):

    def __init__(self, start, end):
        self.itinerary_name = "en trotinette bird"

        scooter = self.__FindScooter(start)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start,scooter), fact.generate_route("electric_bike", scooter, end)]
        ## to do : change speed (scooter is slower than a bike)
        super().__init__(start, end)

    def budget(self):
        return bird_cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff

    def __FindScooter(self, start):
        scooter_lat, scooter_long = bird_find_scooter(start.lat, start.long)
        return models.Point(scooter_lat, scooter_long)


