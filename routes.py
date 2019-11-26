import time
import datetime
from flask import Flask, render_template, request, json

from models.itinerary_factory import *
from models.point import *



app = Flask(__name__)

##Index page
@app.route('/')
def index():
    return render_template('index.html')

##calculate itinerary from form
@app.route('/', methods = ['POST'])
def calculate_itinerary():
    #Recover form parameters
    start = Point(request.form.get('start_lat', type=float), request.form.get('start_long', type=float))
    end = Point(request.form.get('end_lat', type=float), request.form.get('end_long', type=float))

    choix = request.form.get('choice')
    kwargs = {
        "disability_compatible": request.form.get('accessible') != None,
        "rain_compatible": request.form.get('avoid_rain') != None,
        "loaded_compatible": request.form.get('loaded') != None,
        "forbidden_vehicles": request.form.get("forbidden_vehicles").split(',')
    }
#
    #Initialisation d'une factory
    routes = ItineraryFactory()

    #Generation des itineraires
    routes.generate_all_routes(start, end, **kwargs)

    #Trie des itinéraires selon l'ordre choisi par l'utilisateur
    routes.sort(choix)

    #envoi des données en format json au client web
    routes_json = routes.json()
    return json.jsonify(routes_json)
