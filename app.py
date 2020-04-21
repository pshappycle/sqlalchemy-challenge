import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

#Get Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

#Reflect the tables in the database
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#Create Flask
app = Flask(__name__)


#Start and End Dates
present = session.query(measurement.date).order_by(measurement.date.desc()).first()
present_day = present[0]
present_datetime = dt.datetime.strptime(present[0],"%Y-%m-%d")

first_date = present_datetime - dt.timedelta(days=365)
first_day = first_date.strftime("%Y-%m-%d")

session.close()

#Present_day and first_day are my two time values

#Create Flask Routes

@app.route("/")
def home():
    return (
        f"Hello! Welcome to the climate app API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start> <br/>"
        f"/api/v1.0/temp/<start>/<end> <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date > first_day).order_by(measurement.date).all()
    
    precipitation_list = []
    for prcp_data in precipitation_data:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = prcp_data.date
        prcp_data_dict["Precipitation"] = prcp_data.prcp
        precipitation_list.append(prcp_data_dict)
        
    return jsonify(precipitation_list)
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(station.station, station.name).all()
    return jsonify(station_list)
    session.close()


@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    highest_observations = session.query(measurement.station, func.count(measurement.tobs)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    station_highest_observations = highest_observations[0][0]

    tobs_data = session.query(measurement.station, measurement.date, measurement.tobs).filter(measurement.station == station_highest_observations ).filter(measurement.date > first_day)
    
    temp_list = []
    for temp in tobs_data:
        temp_dict ={}
        temp_dict['Station'] = temp.station
        temp_dict['Date'] = temp.date
        temp_dict['Temperature'] = temp.tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)
    session.close()

@app.route("/api/v1.0/temp/<start>")
def start(start=None):
    
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).all()

    start_stats = []
    
    for min, max, avg in results:
        start_dict = {}
        start_dict["Minimum Temp"] = min
        start_dict["Maximum Temp"] = max
        start_dict["Average Temp"] = avg
        start_stats.append(start_dict)
    
    return jsonify(start_stats)
    session.close()

@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start=None, end=None):
    
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    start_end_stats = []
    
    for min, max, avg in results:
        start_end_stats_dict = {}
        start_end_stats_dict["Minimum Temp"] = min
        start_end_stats_dict["Maximum Temp"] = max
        start_end_stats_dict["Average Temp"] = avg
        start_end_stats.append(start_end_stats_dict)
    
    return jsonify(start_end_stats)
    session.close()
if __name__ == "__main__":
    app.run(debug=True)   



