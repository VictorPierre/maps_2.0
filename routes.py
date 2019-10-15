from flask import Flask, render_template, request, json
from models import *


app = Flask(__name__)

##Index page
@app.route('/')
def index():
    available_types= [
        ("foot", "marche"),
        ("bike", "vélo"),
        ("electric_bike", "vélo électrique"),
        ("velib", "Vélib"),
        ("transit", "transports en commun"),
        ("car", "voiture"),
        ("bird", "Bird"),
        ("e-velib","Vélib électrique")
    ]

    data = {'available_types': available_types}
    return render_template('index.html', data=data)

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
    routes = fact.generate_all_routes(start, end) #non multi_threadé
    #routes = fact.generate_all_routes_threads_json(start, end) #tentative de multi_thread

    return json.jsonify(routes)