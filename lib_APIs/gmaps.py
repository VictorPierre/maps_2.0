from dotenv import load_dotenv
load_dotenv()
from os import getenv

import googlemaps

def transit_itinerary(start, end):
    """
    function to find the itinerary in transit thanks to Maps API
    :param start:
    :param end:
    :return:
    """
    duration, distance, geojson = 0, 0, {}

    gmaps = googlemaps.Client(key=getenv("GOOGLE_MAPS_API_KEY"))
    # Request directions via public transit (GoogleMaps)
    directions_result = gmaps.directions(start.to_LatLong(), end.to_LatLong(), mode="transit")

    ##Select the first itinerary
    direction = directions_result[0]['legs'][0]

    duration = direction['duration']['value']
    distance = direction['distance']['value']

    ##Convert to GeoJson
    steps = gmaps_to_geojson(direction['steps'])

    if len(steps)<2:
        raise ValueError('Aucun itinéraire trouvé')

    return duration, distance, steps

def gmaps_to_geojson(steps):
    """
    function to convert the answer of Maps API into a geojson object
    :param steps:
    :return:
    """
    geojson = []
    for step in steps:
        if step["travel_mode"]=="TRANSIT":
            color = step["transit_details"]["line"]["color"]
            coordinates= [[step["start_location"]["lng"], step["start_location"]["lat"]],
                          [step["end_location"]["lng"], step["end_location"]["lat"]]]

        elif step["travel_mode"]=="WALKING":
            color = "#000000"
            coordinates = [[step["start_location"]["lng"], step["start_location"]["lat"]]]
            for substep in step["steps"]:
                coordinates+=[[substep["end_location"]["lng"], substep["end_location"]["lat"]]]

        ##Add the current step to the geojson
        geojson += [{
            'type': 'Feature',
            'properties': {'color': color},
            'geometry': {
                'coordinates': coordinates,
                'type': 'LineString'}}]

    return geojson
