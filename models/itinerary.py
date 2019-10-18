from dotenv import load_dotenv
import os
load_dotenv()
from flask import render_template

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
    def __init__(self, start, end):
        self.cost_per_km=10 #Très conservatif en cas de manque d'information
        self.fixed_cost=5 #Très conservatif en cas de manque d'information
        self.C02_per_km=0 #Si on n'a pas d'information on va partir du principe que la production de C02 est faible (transport en commun, etc...)
        self.calories_per_hour=0 #Si on a pas d'information on va partir du principe que cela n'est pas une activité sportive
        self.rain_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter en cas de pluie
        self.disability_compatible=False #Si on a pas cette information on part du principe qu'il faut éviter si en situation de PMR
        pass

    def html(self):
        return render_template('show.html',
                        name=self.itinerary_name,
                        duration=Itinerary.sec_to_time(self.duration),
                        distance=Itinerary.meter_to_km(self.distance),
                        )

    def json(self):
        return {
            "html": self.html(),
            "geojson": self.geojson,
        }
    def sec_to_time(time):
        time = int(time)
        heure = time//3600
        minute = int((time-heure*3600)//60)
        seconde = int((time - heure*3600 - minute*60))
        if heure == 0 :
            if minute == 0:
                return str(time) + "s"
            else :
                return str(minute)+"mn"
        else :
            return str(heure)+"h"+str(minute)+"mn"

    def meter_to_km(distance):
        distance = int(distance)
        if distance < 1000 :
            return str(distance) + "m"
        else :
            return str(round(distance/1000,1)) + "km"


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
        return "L'itinéraire {} mesure {}m et dure {}.".format(self.itinerary_name,self.distance, self.duration)


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
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de Velib sont les mêmes")
        return models.Point(latA, longA), models.Point(latB, longB)

    def __init__(self, start, end):
        (stationA, stationB) = self.GiveStations(start, end)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start,stationA), fact.generate_route("bike",stationA, stationB), FootItinerary(stationB,end)]
        super().__init__(start, end)
        self.cost = velib_cost(self.duration)
        self.itinerary_name = "Velib"

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
        return Aff

class eVelibItinerary(IndirectItinerary):
    def GiveStations(self, start, end):
        latA, longA = closest_evelib_station(start.lat, start.long)
        latB, longB = closest_evelib_station(end.lat, end.long)
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de eVelib sont les mêmes")

        return models.Point(latA, longA), models.Point(latB, longB)

    def __init__(self, start, end):
        (stationA, stationB) = self.GiveStations(start, end)
        fact = ItineraryFactory()
        self.routes = [FootItinerary(start, stationA), fact.generate_route("electric_bike", stationA, stationB),
                       FootItinerary(stationB, end)]
        super().__init__(start, end)
        self.cost = evelib_cost(self.duration)
        self.itinerary_name = "e-velib"

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
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
        self.itinerary_name = "en trotinette bird"

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff


