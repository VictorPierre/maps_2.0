from flask import Flask, render_template, request
from models import *

app = Flask(__name__)

##Index page
@app.route('/')
def index():
    data = {'available_types': ItineraryFactory.available_types()
            }
    return render_template('index.html', data=data)

##calculate itinerary from form
@app.route('/show', methods = ['POST'])
def foot_itinerary():
    #Recover start & end points from the form
    start_lat = request.form.get('start_lat', type=float)
    start_long = request.form.get('start_long', type=float)
    end_lat = request.form.get('end_lat', type=float)
    end_long = request.form.get('end_long', type=float)
    type = request.form.get('transport')

    #Calculate the best itinerary
    start = Point(start_lat, start_long)
    end = Point(end_lat, end_long)
    fact = ItineraryFactory()
    route = fact.generate_route(type, start, end)

    return render_template('show.html', route=route, geojson="route.geojson")
