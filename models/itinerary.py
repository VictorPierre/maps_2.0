from flask import render_template
import numpy as np

from .point import Point
from .exceptions import *
from lib_APIs import *

class Itinerary:
    """
    ABSTRACT CLASS, implementing the following attributes/methods

    ATTRIBUTES :
    - itinerary_name (string)
    - distance (int type, distance in meters)
    - duration (int type, duration in seconds)
    - geojson (dict, data for visualising the route)
    - grade (our custom grade given considering carbon emissions, cost and duration
    - labels ('green', 'fast', or 'athletic', help to identify best itineraries in a category)
    - rain_compatible (boolean)
    - disability_compatible (boolean)


    METHODS :
    - budget(self) -> float (return the cost in €)
    - carbon_emission(self) -> float (return the CO2 emissions in kg)
    - calories(self) -> float (return the amount of kcal)
    - json(self) -> json (return a JSON containing the geojson + an HTML preview of the itinerary)
    """

    def __init__(self, start, end, **kwargs):
        """
        :param start: point
        :param end: point

        :param rain_compatible: boolean, default : false
        :param disability_compatible: boolean, default : false
        :param loaded_compatible: boolean, default : false
        """
        self.cost_per_km=10 # Très conservatif en cas de manque d'information
        self.fixed_cost=5 # Très conservatif en cas de manque d'information
        self.C02_per_km=0 # Si on n'a pas d'information on va partir du principe que la production de C02 est faible (transport en commun, etc...)
        self.calories_per_hour=0 # Si on a pas d'information on va partir du principe que cela n'est pas une activité sportive
        self.grade=0
        self.labels=[]
        self.rain_compatible=False # Si on a pas cette information on part du principe qu'il faut éviter en cas de pluie
        self.disability_compatible=False # Si on a pas cette information on part du principe qu'il faut éviter si en situation de PMR
        self.loaded_compatible=False

    def budget(self):
        """
        Give the cost (€) for the itinerary
        :return: float
        """
        return float(self.fixed_cost) + float(self.distance)*float(self.cost_per_km)

    def carbon_emission(self):
        """
        Give the CO2 emissions in kg
        (source : http://www.cyclic.info/le-velo-a-assistance-electrique-est-il-polluant/)
        :return: float
        """
        return float(self.distance)/1000*float(self.C02_per_km)

    def calories(self):
        """
        Return the amount of kcal
        :return: float
        """
        return float(self.calories_per_hour)*float(self.duration)/3600

    def json(self):
        """
        Give a JSON containing the geojson + an HTML preview of the itinerary
        :return:json
        """
        return {
            "html": self.__html(),
            "geojson": self.geojson,
        }

    def _check_compatibility(self, **kwargs):
        """
        check if the itinerary is possible given the parameters, and raise error otherwise
        :param kwargs:
        :return:
        """
        if kwargs.get("disability_compatible")==True and not self.disability_compatible:
            raise DisabilityCompatibleException("Impossible de faire de ce moyen de transport en fauteuil roulant")
        if kwargs.get("rain_compatible") == True and not self.rain_compatible:
            raise RainCompatibleException("Ce moyen de transport mouille sous la pluie")
        if kwargs.get("loaded_compatible") == True and not self.loaded_compatible:
            raise LoadedCompatibleException("Impossible de transporter des charges de cette façon")
        if kwargs.get("forbidden_vehicles") and self.name in kwargs.get("forbidden_vehicles"):
            raise ForbiddenVehicleException("Véhicule non autorisé pour cet utilisateur")

    def __html(self):
        """
        Generate an html for rendering the itinerary
        :return:
        """
        return render_template('show.html',
                        name=self.itinerary_name,
                        picture_name = self.picture_name,
                        duration = self.__sec_to_time(),
                        distance = self.__meter_to_km(),
                        rain_compatible = self.rain_compatible,
                        disability_compatible = self.disability_compatible,
                        budget = str(round(self.budget(),2)) + " €",
                        carbon_emission= str(round(self.carbon_emission())) + " g",
                        calories = str(round(self.calories())) + " Kcal",
                        grade = str(round(self.grade,3)),
                        labels = self.labels
                        )

    def __meter_to_km(self):
        """
        Convert self.distance into a pretty format
        :return:
        """
        distance = int(self.distance)
        if distance < 1000 :
            return str(distance) + "m"
        else:
            return str(round(distance / 1000, 1)) + "km"

    def __sec_to_time(self):
        """
        Convert self.duration into a pretty format
        :return:
        """
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


class FootItinerary(Itinerary):
    """
    ITINERAIRES DIRECTS : pas besoin de transiter par une station
    """
    def __init__(self, start, end, **kwargs):
        self.name='foot'
        self.itinerary_name = "à pied"
        self.picture_name = "walker.jpeg"
        # D'après fourchette-et-bikini.fr avec un poids moyen de 70kg
        self.calories_per_hour = 245
        # En prenant en compte qu'une calorie représente 0.2g de CO2 chez l'Homme avec une vitesse d'environ 5km/h
        self.C02_per_km = 0.2*245/5
        self.grade=0
        self.labels = []
        self.rain_compatible = False
        self.disability_compatible = True
        self.loaded_compatible = True

        self._check_compatibility(**kwargs)
        (self.duration,self.distance, self.geojson)= openrouteservice.itinerary(start, end, "foot-walking")

    def budget(self):
        return 0


class BikeItinerary(Itinerary):
    """
    Bike itinerary : itinerary using user's own bike.
    The route is generated with openrouteservice
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'bike'
        self.itinerary_name = "en vélo"
        self.picture_name = "bicycle.png"
        # D'après fourchette-et-bikini.fr avec un poids moyen de 70kg et une vitesse moyenne de 20km/h
        self.calories_per_hour = 560
        # En prenant en compte qu'une calorie représente 0.2g de CO2 chez l'Homme et une vitesse d'environ 20km/h
        self.C02_per_km = 560*0.2/20
        self.grade = 0
        self.labels = []
        self.rain_compatible = False
        self.disability_compatible = False
        self.loaded_compatible = False

        self._check_compatibility(**kwargs)
        (self.duration,self.distance, self.geojson)= openrouteservice.itinerary(start, end, "cycling-regular")
        ##Green color for the geojson
        self.geojson["properties"]["color"]="#026928"

    def budget(self):
        return 0

class ElectricBikeItinerary(Itinerary):
    """
    e-bike itinerary : itinerary using user's own e-bike.
    The route is generated with openrouteservice
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'e-bike'
        self.itinerary_name = "en vélo électrique"
        self.picture_name = "electric-bike.png"
        #On part de l'hypothèse que l'énergie nécessaire est équivalent à marcher pour 20km/h
        self.calories_per_hour = 245
        # En prenant en compte qu'une calorie représente 0.2g de CO2 chez l'Homme et une vitesse d'environ 20km/h pour le premier terme
        # Sachant qu'un vélo éléctrique dépense 500Wh pour faire 120km, avec une vitesse de 20km/h, soit 500/6 Wh/h et que cette production génére 315g/kWh de CO2 en France
        self.C02_per_km = 245*0.2/20 + 500*0.315/6
        self.grade = 0
        self.labels = []
        self.rain_compatible = False
        self.disability_compatible = False
        self.loaded_compatible = True

        self._check_compatibility(**kwargs)
        (self.duration,self.distance, self.geojson)= openrouteservice.itinerary(start, end, "cycling-electric")
        ##Red color for the geojson
        self.geojson["properties"]["color"]="#AA0115"
    def budget(self):
        return 0

class CarItinerary(Itinerary):
    """
    Car itinerary : itinerary using user's own car.
    The route is generated with openrouteservice
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'car'
        self.itinerary_name = "en voiture"
        self.picture_name = "car-compact.png"
        self.calories_per_hour = 0
        # Sachant qu'en moyenne une voiture produit 166g/km d'après transilien.fr
        self.C02_per_km = 166
        self.grade = 0
        self.labels = []
        self.rain_compatible = True
        self.disability_compatible = True
        self.loaded_compatible = True

        self._check_compatibility(**kwargs)
        (self.duration,self.distance, self.geojson)= openrouteservice.itinerary(start, end, "driving-car")
        self.geojson["properties"]["color"]="#AA0115"
    def budget(self):
        #Sachant qu'une voiture moyenne consomme 6.33L/100km et que 1L côute environ 1.5€
        return self.distance*1.5*6.33/100/1000


class TransitItinerary(Itinerary):
    """
    Transit itinerary : itinerary using RATP buses, metros and RERs.
    The route is generated with googlemaps
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'transit'
        self.itinerary_name = "en transports en commun"
        self.picture_name = "bus.png"
        self.calories_per_hour = 0
        # D'après une moyenne pondérée par le nombre d'utilisateurs du Metro, RER, Tramway et Bus à Paris venant de transilien.fr pour la production de C02 par mode et de wikipedia pour la distribution
        self.C02_per_km = 28
        self.grade = 0
        self.labels = []
        self.rain_compatible = True
        self.disability_compatible = False
        self.loaded_compatible = True

        self._check_compatibility(**kwargs)
        (self.duration, self.distance, self.geojson) = gmaps.transit_itinerary(start, end)
    def budget(self):
        #Sachant que le prix d'un ticket à PAris Intra-muros est de 1.9€
        return 1.90


class IndirectItinerary(Itinerary):
    """
    INDIRECT ITINERARIES : an indirect itinerary is a list of direct itineraries
    (ex: walk for 5min and tke a bike for 10min)
    """
    def __init__(self , start, end, **kwargs):
        self.distance = sum([route.distance for route in self.routes])
        self.duration = sum([route.duration for route in self.routes])
        self.geojson = [route.geojson for route in self.routes]
        self.disability_compatible = np.all([route.disability_compatible for route in self.routes])
        self.rain_compatible = np.all([route.rain_compatible for route in self.routes])
        self.loaded_compatible = np.all([route.loaded_compatible for route in self.routes])

    def calories(self):
        return sum([route.calories() for route in self.routes])
    def budget(self):
        return sum([route.budget() for route in self.routes])
    def carbon_emission(self):
        return sum([route.carbon_emission() for route in self.routes])

    def _kwargs_without_forbidden_vehicles(self, kwargs):
        new_kwargs=kwargs.copy()
        new_kwargs.pop("forbidden_vehicles")
        return new_kwargs

class VelibItinerary(IndirectItinerary):
    """
    Velib itinerary : itinerary using velibs
    User will walk to the closest non empty station, take a velib and leave it in a non full station
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'velib'
        self.itinerary_name = "Vélib"
        self.picture_name = "bicycle.png"
        self.grade = 0
        self.labels = []
        (stationA, stationB) = self.__GiveStations(start, end)
        kwargs=self._kwargs_without_forbidden_vehicles(kwargs)
        self.routes = [FootItinerary(start,stationA, **kwargs), BikeItinerary(stationA, stationB, **kwargs), FootItinerary(stationB,end, **kwargs)]
        super().__init__(start, end)

    def budget(self):
        return velib.velib_cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
        return Aff

    def __GiveStations(self, start, end):
        latA, longA = velib.closest_velib_station(start.lat, start.long)
        latB, longB = velib.closest_velib_station(end.lat, end.long)
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de Velib sont les mêmes")
        return Point(latA, longA), Point(latB, longB)


class eVelibItinerary(IndirectItinerary):
    """
    e-Velib itinerary : itinerary using electric velibs
    User will walk to the closest non empty station, take a e-velib and leave it in a non full station
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'e-velib'
        self.itinerary_name = "e-velib"
        self.picture_name = "electric-bike.png"
        self.grade = 0
        self.labels = []
        (stationA, stationB) = self.__GiveStations(start, end)
        kwargs=self._kwargs_without_forbidden_vehicles(kwargs)
        self.routes = [FootItinerary(start, stationA, **kwargs), ElectricBikeItinerary(stationA, stationB, **kwargs),
                       FootItinerary(stationB, end, **kwargs)]

        super().__init__(start, end)

    def budget(self):
        return velib.evelib_cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += "\nTroisième étape:" + str(self.routes[2])
        Aff += ". Le trajet total dure" + str(self.duration)
        return Aff

    def __GiveStations(self, start, end):
        latA, longA = velib.closest_evelib_station(start.lat, start.long)
        latB, longB = velib.closest_evelib_station(end.lat, end.long)
        if (latA, longA) == (latB, longB) :
            raise SameStation ("Les deux stations de eVelib sont les mêmes")

        return Point(latA, longA), Point(latB, longB)

class BirdItinerary(IndirectItinerary):
    """
    Birditinerary : itinerary using Bird scooter
    User will walk to the closest free bird scooter, and leave at his destination
    """
    def __init__(self, start, end, **kwargs):
        self.name = 'bird'
        self.itinerary_name = "en trotinette bird"
        self.picture_name = "scooter.png"
        self.grade = 0
        self.labels = []
        scooter = self.__FindScooter(start)
        kwargs=self._kwargs_without_forbidden_vehicles(kwargs)
        self.routes = [FootItinerary(start,scooter, **kwargs), ElectricBikeItinerary(scooter, end, **kwargs)]
        ## We assume Bird speed is similar to Bike speed which might be optimistic
        super().__init__(start, end)

    def budget(self):
        return bird.cost(self.routes[1].duration)

    def __str__(self):
        Aff = "Première étape:" + str(self.routes[0])
        Aff += "\nDeuxième étape :" + str(self.routes[1])
        Aff += ". Le trajet total dure" + str(self.duration) + "s"
        return Aff

    def __FindScooter(self, start):
        scooter_lat, scooter_long = bird.find_scooter(start.lat, start.long)
        return Point(scooter_lat, scooter_long)


