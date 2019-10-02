##LOAD CLASSES
from models import *
from flask import Flask
from routes import *


if __name__ == "__main__":

    print('Bienvenue dans Maps 2.0')
    start = Point(48.8327878, 2.3380036)
    end = Point(48.8450477, 2.3419488)
    fact = ItineraryFactory()

    print(ItineraryFactory.available_types())

    ##foot route
    #route=fact.generate_route("foot", start, end)
    route=FootItinerary(start,end)
    print(route)

    ##Bike routeq
    route = fact.generate_route("bike", start, end)
    print(route)

    #Electric Bike route
    route = fact.generate_route("electric_bike", start, end)
    print(route)

    ##Car route
    #route = fact.generate_route("car", start, end)
    #print(route)

    ##Velib route
    route=fact.generate_route("velib", start, end)
    print(route)

    ##Bird scooter route
    route=fact.generate_route("bird", start, end)
    print(route)

    #googlemaps transit route
    #route=TransitItinerary(start,end)
    #route = fact.generate_route("transit", start, end)
    #print(route)

    ##Launch web app
    #app.run()