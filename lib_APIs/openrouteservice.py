from dotenv import load_dotenv
load_dotenv()
from os import getenv
import requests
from .exceptions import *

def itinerary(start, end, means_of_transport,open_route_api_key=getenv("OPEN_ROUTE_SERVICE_API_KEY")):
    """
    function to get itinerary in car, electric bike, bike, scooter or walking thanks to openrouteservice API
    :param start:
    :param end:
    :param means_of_transport:
    :param open_route_api_key:
    :return:
    """

    duration, distance, geojson = 0, 0, {}
    ##Call the API only if the start and end are 2 different points
    if not start == end:
        ##API CALL
        params = {'api_key': open_route_api_key, 'start': start.to_LongLat(), 'end': end.to_LongLat()}
        req="https://api.openrouteservice.org/v2/directions/"+str(means_of_transport)
        reponse = requests.get(req, params=params)
        if reponse.status_code!=200:
            raise ApiException("OpenRouteService API error\nStatus code : {}\n Body: {}".format(reponse.status_code, reponse.json()))
        resp = reponse.json()
        if len(resp['features'])==0 or len(resp['features'][0]["properties"]['segments'])==0:
            raise ValueError('Aucun itinéraire trouvé')
        duration = resp['features'][0]["properties"]['segments'][0]['duration']
        distance = resp['features'][0]["properties"]['segments'][0]['distance']
        geojson = resp['features'][0]
    return duration, distance, geojson













