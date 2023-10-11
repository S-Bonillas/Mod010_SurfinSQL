# Import the dependencies.
import datetime as dt
import numpy as np
import json


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from flask import Flask, Response

# Create the engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Setup Flask
app = Flask(__name__)

# Create welcome page for the API.
@app.route("/")
def welcome():
    return(
        f"Aloha. This is the Hawaiian Climate Analysis API.<br/>"
        f"Available routes are listed below: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>The 'start' and 'end' dates should be formatted MMDDYYYY.</p>"
        f"<p>Note: '/api/v1.0/tobs' returns the temperatures recorded at the most active station.</p>"
    )

# Create links into the database.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    precip = { date: prcp for date, prcp in precipitation}

    # Creating Custom response to give context to the returned data
    custom_response_precip = {
        "Message": f"Displaying date of collection and the Precipitation amount (inches).",
        "Precipitation ([Date]:[Precip Amount])": precip
    }

    return jsonify(custom_response_precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    # Creating Custom response to give context to the returned data
    custom_response_stations = {
        "Message": f"Stations Providing Data to this API",
        "Reporting Stations": stations
    }

    return jsonify(custom_response_stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    session.close()

    print()

    temps = list(np.ravel(results))

    # Creating Custom response to give context to the returned data
    custom_response_tobs = {
        "Message": f"Temperatures recorded by most active station (USC00519281)",
        "Temperatures (f)": temps
    }

    return jsonify(custom_response_tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        # Creating Custom response to give context to the returned data
        temps = list(np.ravel(results))
        
        min_temp, avg_temp, max_temp = temps
        
        custom_response_start = {
            "Message": f"Returning the Min, Avg, and Max Temperatures from the Requested Start Date to end of the dataset.",
            "Requested Start Date": start.strftime("%m%d%Y"),
            "Minimum Temperature (f)": min_temp,
            "Average Temperature (f)": avg_temp,
            "Maximum Temperature (f)": max_temp
        }

        json_response_start = json.dumps(custom_response_start, indent=4)

        return Response(json_response_start, content_type="application/json; charset=utf-8")
    
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    # Creating Custom response to give context to the returned data
    temps = list(np.ravel(results))
    
    min_temp, avg_temp, max_temp = temps
    
    custom_response_start_end = {
        "Message": f"Returning the Min, Avg, and Max Temperatures from the Requested Start Date to Requested End Date.",
        "Requested Start Date": start.strftime("%m%d%Y"),
        "Requested End Date": end.strftime("%m%d%Y"),
        "Minimum Temperature (f)": min_temp,
        "Average Temperature (f)": avg_temp,
        "Maximum Temperature (f)": max_temp
        }

    json_response_start_end = json.dumps(custom_response_start_end, indent=4)

    return Response(json_response_start_end, content_type="application/json; charset=utf-8")

# Run debugger
if __name__ == "__main__":
    app.run(debug=True)
