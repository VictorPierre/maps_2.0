import time
import datetime
from threading import Thread
from multiprocessing import Queue
from statistics import *

from .itinerary import *
from .exceptions import *
from lib_APIs.exceptions import *

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
            "car": CarItinerary,
            "bird": BirdItinerary,
        }
        self._sort_methods = {
            "duration": self.__sort_by_duration,
            "distance": self.__sort_by_distance,
            "co2": self.__sort_by_co2,
            "calories": self.__sort_by_calories_asc,
            "sport": self.__sort_by_calories_des,
        }
        self.routes = []

    def json(self):
        json = []
        for route in self.routes:
            json.append(route.json())
        return json

    def generate_route(self, type, start, end, out_queue, **kwargs):
        builder = self._builders.get(type)
        if builder is None:
            raise ValueError(type)
        try:
            out_queue.put(builder(start, end, **kwargs))
        except (RainCompatibleException, LoadedCompatibleException, DisabilityCompatibleException, SameStation) as e:
            print(e)
        except (ValueError, ApiException) as e:
            print("Impossible de générer l'itinéraire :")
            print(e)


    def generate_all_routes(self, start, end, **kwargs):
        my_queue=Queue()
        threads=[]
        tmpsstart=[]
        tmpsend=[]
        tmpsdiff=[]
        tmpssum=datetime.timedelta()

        #Creation des threads pour chaque type d'itinéraire
        for builder in self._builders:
            thread = Thread(target=self.generate_route, args=(builder,start,end,my_queue), kwargs=kwargs)
            threads.append(thread)

        #Démarrage de chaque thread
        for thread in threads:
            tmpsstart.append(datetime.datetime.now())
            thread.start()

        #Pour chaque thread on précise la nécessité d'attendre les autres avant d'avancer
        for thread in threads:
            thread.join()
            tmpsend.append(datetime.datetime.now())

        #Vérification de la pertinence temporelle du multi-thread
        #for i in range (len(tmpsstart)):
         #   tmpsdiff.append(tmpsend[i]-tmpsstart[i])
         #   tmpssum+=tmpsdiff[-1]
        #print("La sommation des temps totaux pour l'appel et le retour aux APIs pour est de {}".format(tmpssum))

        #tmps1 = datetime.datetime.now()

        #Reprend les infos dans la queue venant des threads
        while int(my_queue.qsize())>0 :

            self.routes.append(my_queue.get())
        #tmps2 = datetime.datetime.now()
        #print("Le temps total pour le dépilage de la queue est de {}".format(tmps2 - tmps1))

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
        self.routes.sort(key=lambda x: x.grade, reverse=False)



    def grade(self, choix):
        grademethod = self._grade_methods.get(choix)
        if grademethod is None:
            raise ValueError(choix)
        grademethod()

    def grade_by_duration(self):
        duration = [route.distance for route in self.routes]
        print(duration)
        pass

    #def __grade_by_distance(self):
     #   self.routes.mean(key=lambda x: x.distance, reverse=False)
      #  pass




