##LOAD CLASSES
from models import *
from flask import Flask
from routes import *

if __name__ == "__main__":

    print('Bienvenue dans Maps 2.0')
    start = Point(48.8327878, 2.3380036)
    end = Point(48.8450477, 2.3419488)

    Station = VelibItinerary.Station_plus_proche(start)
    print(Station.lat,Station.long)
    route = VelibItinerary(start,end)

    ##foot route
    route=FootItinerary(start,end)
    print(route)

    ##Bike route
    route=BikeItinerary(start,end)
    print(route)

    #Electric Bike route
    route=ElectricBikeItinerary(start,end)
    print(route)

    ##Car route
    route=CarItinerary(start,end)
    print(route)

    #googlemaps transit route
    #route=TransitItinerary(start,end)
    #print(route)

    ##Launch web app
    app.run()



