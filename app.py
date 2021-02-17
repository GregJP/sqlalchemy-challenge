import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

climate_base = automap_base()
climate_base.prepare(engine, reflect=True)

meas = climate_base.classes.measurement
stat = climate_base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the home page.<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start(YYYY-MM-DD)<br/>"
        f"/api/v1.0/start(YYYY-MM-DD)/end(YYYY-MM-DD)")
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returning a dictionary of dates and precipation values."""
    session = Session(engine)
    results = session.query(meas.date,meas.prcp).all()
    session.close()
    
    date_prcp = []
    for date, prcp in results:
        meas_dict = {}
        meas_dict["date"] = date
        meas_dict["prcp"] = prcp
        date_prcp.append(meas_dict)
    
    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Returning a list of all of the stations."""
    session = Session(engine)
    results = session.query(stat.station).all()
    session.close()
    
    station_list = list(np.ravel(results))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returning list of temperatures for most active station within last year of data."""
    session = Session(engine)
    results = session.query(meas.date,meas.tobs).filter(meas.date >= '2016-08-23').filter(meas.station == 'USC00519281').all()
    session.close()
    
    station_tobs = list(np.ravel(results))

    return jsonify(station_tobs)

@app.route("/api/v1.0/<start>/<end>")
def date_search(start,end):
    """Returning temperature stats on dates based on user input"""
    if end == "":    
        session = Session(engine)
        results = session.query(func.min(meas.tobs),func.max(meas.tobs),func.avg(meas.tobs)).filter(meas.date >= str(start)).all()
        session.close()
    else:
        session = Session(engine)
        results = session.query(func.min(meas.tobs),func.max(meas.tobs),func.avg(meas.tobs)).filter(meas.date >= str(start)).filter(meas.date <= str(end)).all()
        session.close()        
#     tmin = func.min(results)
#     tmax = func.max(results)
#     tavg = func.avg(results)
#     search_results = [tmin,tmax,tavg]

    tobs_stats = list(np.ravel(results))
    
    return jsonify(tobs_stats)
# Not sure why it's resulting in 404
    
if __name__ == "__main__":
    app.run(debug=True)