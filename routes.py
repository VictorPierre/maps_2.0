from flask import Flask, render_template, request, json
from models import *
from lib.weather import *
import time
import datetime

app = Flask(__name__)

##Index page
@app.route('/')
def index():
    return render_template('index.html', HasPrecipitation=HasPrecipitation())

##calculate itinerary from form
@app.route('/', methods = ['POST'])
def calculate_itinerary():
    #Recover start & end points from the form
    start_lat = request.form.get('start_lat', type=float)
    start_long = request.form.get('start_long', type=float)
    end_lat = request.form.get('end_lat', type=float)
    end_long = request.form.get('end_long', type=float)

    #Calculate the best itinerary
    start = Point(start_lat, start_long)
    end = Point(end_lat, end_long)

    fact = ItineraryFactory()
    tmps1 = datetime.datetime.now()

    #fact.generate_all_routes(start, end) #non multi_thread           # Temps d'execution 0:00:02.472217
    routes = fact.generate_all_routes_threads_json(start, end)#multi_thread # Temps d'execution 0:00:01.599014
    routes.sort_by_duration()
    routes = routes.json()

    tmps2 = datetime.datetime.now()
    print("Le temps total pour les appels et retours aux API est de {}".format(tmps2-tmps1))
    return json.jsonify(fact.json())
