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

app_alpha = TimeSeries("Alpha_Advantage_key")

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

funds_available = 10000
funds = format(funds_available, ",")

mongo = PyMongo(app)

stock_aapl = app_alpha.get_daily_adjusted("AAPL")

dayValidator = datetime.now().strftime('%w')

if dayValidator == '0':
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
elif dayValidator == '1':
    yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
else:
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

transactions = mongo.db.transactions.find()

transaction_lst = []

for transaction in transactions:
    transaction_lst.append(transaction)

profit_loss_lst = []

for item in transaction_lst:
    profit_loss_lst.append(
        round(((float(item['purchase_price']) -
        float(stock_aapl[0][yesterday]['4. close'])) *
        int(item['stock_amount'])), 2))


print(sum(profit_loss_lst))
