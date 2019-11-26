import time
import logging
from threading import Thread
from multiprocessing import Queue
from statistics import *

from .itinerary import *
from .exceptions import *
from lib_APIs.exceptions import *
from lib_APIs import accuweather

class ItineraryFactory:
    """
    Class that contains all the different routes for a given start and end
    """
    def __init__(self):
        self._builders = {
            "foot": FootItinerary,
            "bike": BikeItinerary,
            "electric_bike": ElectricBikeItinerary,
            "velib": VelibItinerary,
            "e-velib": eVelibItinerary,
            "transit": TransitItinerary,
            "uber": UberItinerary,
            "car": CarItinerary,
            "bird": BirdItinerary,
        }
        self._sort_methods = {
            "duration": self.__sort_by_duration,
            "distance": self.__sort_by_distance,
            "co2": self.__sort_by_co2,
            "calories": self.__sort_by_calories_asc,
            "sport": self.__sort_by_calories_des,
            "grade": self.__sort_by_grade,
        }
        self.routes = []

    def json(self):
        ##Calculates optionnal arguments (weather)
        kwargs={}
        try:
            kwargs["rain_risk"]=accuweather.HasPrecipitation()
        except ApiException as e:
            logging.warning("API exception :" + str(e))

        ##generate a json for each itinerary
        json = []
        for route in self.routes:
            json.append(route.json(**kwargs))
        return json

    def generate_route(self, type, start, end, out_queue, **kwargs):
        """
        Creates a route with the calculation made in a new thread in order to minimize response time

        :param type:
        :param start:
        :param end:
        :param out_queue: Queue to centralize information of the different threads
        :param kwargs:
        :return:
        """
        builder = self._builders.get(type)
        if builder is None:
            raise ValueError(type)
        try:
            out_queue.put(builder(start, end, **kwargs))
            logging.info(type.upper()+" itinerary successfully generated")
        except (RainCompatibleException, LoadedCompatibleException, DisabilityCompatibleException, SameStation, ForbiddenVehicleException) as e:
            logging.info(type.upper()+" itinerary not generated\n"+str(e))
        except (ValueError, ApiException) as e:
            logging.warning(type.upper()+" itinerary error\n"+ str(e))


    def generate_all_routes(self, start, end, **kwargs):
        """
        Creates all routes with each routes in a different thread to minimize response time

        :param start:
        :param end:
        :param kwargs:
        :return:
        """
        my_queue=Queue()
        threads=[]

        #Creation des threads pour chaque type d'itinéraire
        for builder in self._builders:
            thread = Thread(target=self.generate_route, args=(builder,start,end,my_queue), kwargs=kwargs)
            threads.append(thread)

        #Démarrage de chaque thread
        for thread in threads:
            thread.start()

        #Pour chaque thread on précise la nécessité d'attendre les autres avant d'avancer
        for thread in threads:
            thread.join()

        #Reprend les infos dans la queue venant des threads
        while int(my_queue.qsize())>0 :
            self.routes.append(my_queue.get())

        #computes grades for each itinerary
        self.__grade_all()
        #give labels (ex: fastest, best...)
        self.__set_labels()

    def sort(self, choix):
        sortmethod = self._sort_methods.get(choix)
        if sortmethod is None :
            raise ValueError(choix)
        sortmethod()

    def __sort_by_duration(self):
        self.routes.sort(key=lambda x: x.duration, reverse=False)
        pass
    def __sort_by_distance(self):
        self.routes.sort(key=lambda x: x.distance, reverse=False)
        pass
    def __sort_by_co2(self):
        self.routes.sort(key=lambda x: x.carbon_emission(), reverse=False)
        pass
    def __sort_by_calories_asc(self):
        self.routes.sort(key=lambda x: x.calories(), reverse=False)
        pass
    def __sort_by_calories_des(self):
        self.routes.sort(key=lambda x: x.calories(), reverse=True)
        pass
    def __sort_by_grade(self):
        self.routes.sort(key=lambda x: x.grade, reverse=True)

    def __grade(self, route, durations, calories, CO2, prices):
        """
        Calculates the grade of a route
        :param route:
        :param durations:
        :param calories:
        :param CO2:
        :param prices:
        :return:
        """
        duration_grade = 0 if max(durations)==0 else -route.duration/max(durations)
        carbon_grade = 0 if max(CO2) else -route.carbon_emission()/max(CO2)
        cost_grade = 0 if max(prices)==0 else -route.budget()/max(prices)
        calories_grade = 0 if max(calories)==0 else route.calories()/max(calories)
        return 2*duration_grade + carbon_grade + cost_grade + calories_grade

    def __grade_all(self):
        """
        Methode qui génère une note pour chacune des routes
        :return:
        """
        if len(self.routes)==0:
            return
        durations=[route.duration for route in self.routes]
        calories=[route.calories() for route in self.routes]
        CO2=[route.carbon_emission() for route in self.routes]
        prices=[route.budget() for route in self.routes]

        for route in self.routes:
            route.grade=self.__grade(route, durations, calories, CO2, prices)

    def __set_labels(self):
        """
        Create the labels 'fast', 'green', 'selection' and 'athletic' for the best itineraries
        :return:
        """
        if len(self.routes)==0:
            return
        else:
            fastest_route, greenest_route, most_athletic_route, best_route = self.routes[0],self.routes[0],self.routes[0],self.routes[0]
            for route in self.routes:
                if route.duration<fastest_route.duration:
                    fastest_route=route
                if route.carbon_emission()<greenest_route.carbon_emission():
                    greenest_route=route
                if route.calories()>most_athletic_route.calories():
                    most_athletic_route=route
                if route.calories()>best_route.grade:
                    best_route=route
            fastest_route.labels.append({"name":"Le plus rapide", "picture": "fastest.png"})
            most_athletic_route.labels.append({"name":"Le choix fitness", "picture": "healthy.png"})
            greenest_route.labels.append({"name":"Le choix éco", "picture": "eco-friendly.png"})
            greenest_route.labels.append({"name":"Meilleur itinéraire", "picture": "selection.png"})