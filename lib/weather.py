from dotenv import load_dotenv
import os
load_dotenv()
import requests
from lib.Exception import *


#function that returns a boolean to know if there is going to have any precipitation in the following hour
def HasPrecipitation():
    url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/623?"
    data = {"apikey":os.getenv("WEATHER_API_KEY")}
    reponse = requests.get(url, params=data)
    if reponse.status_code != 200 :
        raise ApiException ('\nAPI Weather ne répond pas:\n Message: '+reponse.json()['Message'])
    resp = reponse.json()
    return resp[0]["HasPrecipitation"]

