from dotenv import load_dotenv
import os
load_dotenv()
import requests
import lib.API_Exception

def openrouteservice_itinerary(start, end, means_of_transport,open_route_api_key=os.getenv("OPEN_ROUTE_SERVICE_API_KEY")):
    duration, distance = 0, 0
    ##Call the API only if the start and end are 2 different points
    if not start == end:
        ##API CALL
        params = {'api_key': "open_route_api_key", 'start': start.to_LongLat(), 'end': end.to_LongLat()}
        req="https://api.openrouteservice.org/v2/directions/"+str(means_of_transport)
        reponse = requests.get(req, params=params)
        if reponse.status_code!=200:
            raise Exception("OpenRouteService API error\nStatus code : {}\n Body: {}".format(reponse.status_code, reponse.json()))
        else:
            ##If response == 200, recover duration and distance from the request body
            resp = reponse.json()
            duration = resp['features'][0]["properties"]['segments'][0]['duration']
            distance = resp['features'][0]["properties"]['segments'][0]['distance']
            geojson = resp['features'][0]
    return duration, distance


