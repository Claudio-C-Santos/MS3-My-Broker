import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from alpha_vantage.timeseries import TimeSeries
from flask_pymongo import PyMongo
from datetime import date, datetime, timedelta
from support import app, mongo, app_alpha, stock_aapl

# Yesterday Selector
# Since the API only provides yesterday's stock prices,
# the if statement takes into consideration weekends because no price
# is available during these days.
# Instead it provides the last available prices
dayValidator = datetime.now().strftime('%w')

if dayValidator == '0':
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
elif dayValidator == '1':
    yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
else:
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

initial_funds = 10000


# Function used to retrieve the username string from session['user']
def getUsername(session):
    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return username


# Function used to calculate the amount of funds left
# The function uses a database on MongoDB where all the transactions are store,
# then it just adds or substracts them to the initial 10k
def wallet():
    wallet_transactions = mongo.db.wallet_transactions.find()

    wallet_statements = []

    for statements in wallet_transactions:
        if session['user'] == statements['created_by']:
            wallet_statements.append(statements['money_amount'])

    # account's funds
    funds = initial_funds + sum(wallet_statements)

    return funds


# Function used to transform numbers into string and add the thousand's comma
def stringify_number(el):
    element = format(round(el, 2), ",")
    return element


# Function used to access all the transactions sotre in MongoDB's database
def transactions():
    # Retrieve all data from mongoDB's "transactions" entries
    transactions = mongo.db.transactions.find()
    return transactions


# Function based ont transactions() but it provides a list of transactions
# This is so to make possible access each key:value pairs
def transaction_lst(session):
    # Retrieve all data from mongoDB's "transactions" entries
    transactions = mongo.db.transactions.find()

    # Object where each transaction is appended to from the for loop
    transaction_lst = []

    for items in transactions:
        if session['user'] == items['created_by']:
            transaction_lst.append(items)

    return transaction_lst


def profit_loss(session):
    # Retrieve all data from mongoDB's "transactions" entries
    transactions = mongo.db.transactions.find()

    # Object where each transaction is appended to from the for loop
    transaction_lst = []

    for items in transactions:
        if session['user'] == items['created_by']:
            transaction_lst.append(items)

    profit_loss_lst = []

    for item in transaction_lst:
        profit_loss_lst.append(
            round(((
                float(stock_aapl[0][yesterday]['4. close']) -
                float(item['purchase_price'])) *
                int(item['stock_amount'])), 2))

    return sum(profit_loss_lst)
