##LOAD CLASSES
from point import *
from itinerary import *


if __name__ == "__main__":
    print('Bienvenue dans Maps 2.0')

    start = Point(8.681495, 49.41461)
    end = Point(8.687872,49.420318)

    route=FootItinerary(start,end)
    print(route.duration)
    print(route.distance)
