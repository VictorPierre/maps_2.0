from flask import Flask, render_template, request
from models import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/foot', methods = ['POST'])
def foot_itinerary():
    #Recover start & end points from the form
    start_lat = request.form.get('start_lat', type=float)
    start_long = request.form.get('start_long', type=float)
    end_lat = request.form.get('end_lat', type=float)
    end_long = request.form.get('end_long', type=float)

    #Calculate the best itinerary
    start = Point(start_lat, start_long)
    end = Point(end_lat, end_long)
    route=FootItinerary(start,end)

    return str(route)
