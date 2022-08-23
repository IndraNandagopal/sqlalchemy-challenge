#Design a Flash API for Climate APP
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, date, time

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save reference to the table
Measurements = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# List all Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )

#precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most reent date from measurement table
    recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    precipitation_results = session.query(Measurements.date, Measurements.prcp)\
                                    .filter(Measurements.date >= year_ago)\
                                    .filter(Measurements.date <= dt.date(2017,8,23))\
                                    .order_by(Measurements.date).all()
                                 
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation_data = []
    for date, prcp in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

#station route

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all station names from station table
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))
    return jsonify(station_list)

#tobs route

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the previous year of data."""
    results = session.query(Measurements.date, Measurements.tobs)\
                            .filter(Measurements.station == 'USC00519281')\
                            .filter(Measurements.date >= '2016-08-23')\
                            .order_by(Measurements.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of temperature observation
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperature_data.append(temperature_dict)
    
    return jsonify(temperature_data)


#start / end date route
#calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or 
# equal to the start date and less than or equal to the end date.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Query for min, max, and avg temperature for all dates greater than or equal to the start date
    and less than or equal to end date"""
    if not end:
        results = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),\
                              func.avg(Measurements.tobs))\
                              .filter(Measurements.date >= start).all()
        # Create a dictionary from the row data and append to a list of temperature observation
        temp_data_startToEnd = []
        for min,max,avg in results:
            temp_dict_startToEnd = {}
            temp_dict_startToEnd["TMIN"] = min
            temp_dict_startToEnd["TMAX"] = max
            temp_dict_startToEnd["TAVG"] = avg
            temp_data_startToEnd.append(temp_dict_startToEnd)
        
        return jsonify(temp_data_startToEnd)                    
                              
    results = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),\
                              func.avg(Measurements.tobs))\
                              .filter(Measurements.date >= start)\
                              .filter(Measurements.date <= end).all()
       
    # Create a dictionary from the row data and append to a list of temperature observation
    temp_data_startToEnd = []
    for min,max,avg in results:
        temp_dict_startToEnd = {}
        temp_dict_startToEnd["TMIN"] = min
        temp_dict_startToEnd["TMAX"] = max
        temp_dict_startToEnd["TAVG"] = avg
        temp_data_startToEnd.append(temp_dict_startToEnd)
    
    return jsonify(temp_data_startToEnd)

    session.close()
#################################################
if __name__ == '__main__':
    app.run(debug=True)