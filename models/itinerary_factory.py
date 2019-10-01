from .itinerary import *

class ItineraryFactory:
    def generate_route(self, type, start, end):
        generator = get_generator(type)
        return generator(start, end)


def get_generator(type):
    if type == 'foot':
        return FootItinerary
    elif type == 'transit':
        return TransitItinerary
    elif type == 'bike':
        return BikeItinerary
    elif type == 'velib':
        return VelibItinerary
    else:
        raise ValueError('Moyen de transport inconnu')
