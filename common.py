import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from alpha_vantage.timeseries import TimeSeries
from flask_pymongo import PyMongo
from datetime import date, datetime, timedelta

# instancing Flask
app = Flask(__name__)

# instancing Alpha Advantage API in order to retrieve quotes
app_alpha = TimeSeries("Alpha_Advantage_key")

# instancing access to MongoDB database
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

mongo = PyMongo(app)

# Retrieve stock info from Alpha Advantage API
stock_aapl = app_alpha.get_daily_adjusted("AAPL")

# Yesterday Selector
dayValidator = datetime.now().strftime('%w')

if dayValidator == '0':
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
elif dayValidator == '1':
    yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
else:
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def getUsername(session):
    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return username


def wallet():
    wallet_transactions = mongo.db.wallet_transactions.find()

    wallet_statements = []

    for statements in wallet_transactions:
        if session['user'] == statements['created_by']:
            wallet_statements.append(statements['money_amount'])

    # account's funds
    initial_funds = 10000
    funds = initial_funds + sum(wallet_statements)

    return funds


def stringify_number(el):
    funds_available = format(round(el, 2), ",")
    return funds_available


def transactions():
    # Retrieve all data from mongoDB's "transactions" entries
    transactions = mongo.db.transactions.find()
    return transactions


def transaction_lst(session):
    # Retrieve all data from mongoDB's "transactions" entries
    transactions = mongo.db.transactions.find()

    # Object where each transaction is appended to from the for loop
    transaction_lst = []

    for items in transactions:
        transaction_lst.append(items)

    profit_loss_lst = []

    for item in transaction_lst:
        profit_loss_lst.append(
            round(((
                float(stock_aapl[0][yesterday]['4. close']) -
                float(item['purchase_price'])) *
                int(item['stock_amount'])), 2))

    return transaction_lst
