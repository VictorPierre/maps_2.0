from dotenv import load_dotenv
import os
load_dotenv()
import requests

def HasPrecipitation():
    url = "http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/623?"
    data = {"apikey":os.getenv("WEATHER_API_KEY")}
    reponse = requests.get(url, params=data)
    if reponse.status_code != 200 :
        raise ApiException ('API Weather ne répond pas')
    resp = reponse.json()

    return resp[0]["HasPrecipitation"]

