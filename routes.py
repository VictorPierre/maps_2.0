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

    routes = ItineraryFactory()
    # Commentaries are here in case the time necessary for a response needs to be measured
    # tmps1 = datetime.datetime.now()

    routes.generate_all_routes(start, end, **kwargs)#multi_thread # Temps d'execution 0:00:01.599014

    routes.sort(choix) #on trie les routes selon le choix selectionné par l'utilisateur sur l'interface web

    routes_json = routes.json()

    # tmps2 = datetime.datetime.now()
    # print("Le temps total pour les appels et retours aux API est de {}".format(tmps2-tmps1))
    return json.jsonify(routes_json)
