import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from alpha_vantage.timeseries import TimeSeries
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

mongo = PyMongo(app)


def getUsername(session):
    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return username
