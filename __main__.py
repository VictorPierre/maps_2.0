##LOAD CLASSES
from models import *
from flask import Flask
from routes import *

if __name__ == "__main__":

    print('Bienvenue dans Maps 2.0')
    start = Point(48.8327878, 2.3380036)
    end = Point(48.8450477, 2.3419488)

    #fact = ItineraryFactory()
    ##foot route
    #route=FootItinerary(start,end)
    #print(route)
    #route=fact.generate_route("foot", start, end)
    #print(route)

    #googlemaps transit route
    #route=TransitItinerary(start,end)
    #print(route)

    ##Launch web app
    app.run()



