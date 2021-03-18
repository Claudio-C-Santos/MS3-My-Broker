import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from alpha_vantage.timeseries import TimeSeries
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

# instancing Flask
app = Flask(__name__)

# instancing Alpha Advantage API in order to retrieve quotes
app_alpha = TimeSeries("Alpha_Advantage_key")

# instancing access to MongoDB database
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("secret_key")

mongo = PyMongo(app)

# Retrieve stock info from Alpha Advantage API
stock_aapl = app_alpha.get_daily_adjusted("AAPL")