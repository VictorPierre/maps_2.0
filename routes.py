from flask import Flask, render_template, request, json
from models import *
from lib.weather import *


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
    fact.generate_all_routes(start,end)
    routes = fact.json() #non multi_threadé
    #routes = fact.generate_all_routes_threads_json(start, end) #tentative de multi_thread

    return json.jsonify(routes)