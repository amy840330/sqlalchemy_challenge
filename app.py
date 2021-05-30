from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd

# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station


app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
            )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all date and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def temperature():

 # Create our session (link) from Python to the DB
    session = Session(engine)

# Query date and temperature in the past year from the most active station

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > '2016-08-22').\
    filter(Measurement.date < '2017-08-24').\
    filter(Measurement.station=="USC00519281").all()

    session.close()

    all_temperature = []
    for date, tobs in results:
         temperature_dict = {}
         temperature_dict["date"] = date
         temperature_dict["temperature"] = tobs
         all_temperature.append(temperature_dict)

    return(jsonify(all_temperature))

@app.route("/api/v1.0/<start>")
def startdate(start):

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).all()
    
    session.close()
    
    df=pd.DataFrame(results)


    if start in df.values:

       
        df2=df.loc[(df.iloc[:,0]>start),1]

        TMIN=df2.min()
        TMAX=df2.max()
        TAVG=df2.mean()

        data = [{
                    "Minimum Temperature": TMIN,
                    "Maximum Temperature": TMAX,
                    "Average Temperature": TAVG
           }]

        return jsonify(data)

    

    return jsonify({"error": f"The date you are searching is not found."}), 404


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).all()
    
    session.close()
    
    df=pd.DataFrame(results)


    if start in df.values and end in df.values and end>start:

       
        df2=df.loc[((df.iloc[:,0]>start) & (df.iloc[:,0]<=end)),1]

        TMIN=df2.min()
        TMAX=df2.max()
        TAVG=df2.mean()

        data = [{
                    "Minimum Temperature": TMIN,
                    "Maximum Temperature": TMAX,
                    "Average Temperature": TAVG
           }]

        return jsonify(data)

    

    return jsonify({"error": f"The date you are searching {start} is not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)