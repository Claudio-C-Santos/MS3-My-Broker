import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from alpha_vantage.timeseries import TimeSeries
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app_alpha = TimeSeries("Q6C1O1J04IYQXEUN")

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_transactions")
def get_transactions():
    transactions = mongo.db.transactions.find()
    stock = app_alpha.get_daily_adjusted("AAPL")
    return render_template("transactions.html", transactions=transactions, stock=stock)


if __name__ ==   "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
