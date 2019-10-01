from dotenv import load_dotenv
import os
load_dotenv()
import requests

def openrouteservice_itinerary(start, end, means_of_transport,open_route_api_key=os.getenv("OPEN_ROUTE_SERVICE_API_KEY")):
    params = {'api_key': open_route_api_key, 'start': start.to_LongLat(), 'end': end.to_LongLat()}
    req="https://api.openrouteservice.org/v2/directions/"+str(means_of_transport)
    reponse = requests.get("https://api.openrouteservice.org/v2/directions/foot-walking", params=params)
    resp = reponse.json()
    duration = resp['features'][0]["properties"]['segments'][0]['duration']
    distance = resp['features'][0]["properties"]['segments'][0]['distance']
    return(duration,distance)

