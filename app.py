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
from common import yesterday, getUsername, wallet, transactions
from common import transaction_lst, stringify_number
from common import profit_loss
from support import app, mongo, app_alpha, stock_aapl


# Decorator created to render the index page
@app.route("/")
def index():
    return render_template("index.html")


# Decorator created to store the user's registration in MongoDB
# After registering the user is redirected to profile page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
                        {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # Form to be inserted into Mongo's database
        # These are inputs in the register form
        register = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # Inserts "register"
        mongo.db.users.insert_one(register)

        # Variable created to pass in render_template to
        # display on profile page
        session["user"] = request.form.get("username").lower()

        # Variable created to pass in render_template
        # to display on profile page
        first_name = mongo.db.users.find_one(
            {"username": session["user"]})["first_name"]

        return render_template(
                               "profile.html",
                               username=session["user"],
                               first_name=first_name,
                               transactions=transactions,
                               transaction_lst=transaction_lst(session),
                               stock_aapl=stock_aapl,
                               yesterday=yesterday,
                               funds_available=stringify_number(wallet()),
                               profit_loss=stringify_number(
                                   profit_loss(session)))

    return render_template("register.html")


# Decorator created to authenticate the login submitted byt the user
# Once verified the user is redirected to profile page otherwise a
# flash message will be displayed
@app.route("/login", methods={"GET", "POST"})
def login():
    if request.method == "POST":
        # check if username is in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # confirm password
            if check_password_hash(
                                   existing_user["password"],
                                   request.form.get("password")):
                session["user"] = request.form.get("username").lower()

                first_name = mongo.db.users.find_one(
                    {"username": session["user"]})["first_name"]

                return render_template(
                    "profile.html",
                    username=session["user"],
                    first_name=first_name,
                    transactions=transactions(),
                    transaction_lst=transaction_lst(session),
                    stock_aapl=stock_aapl,
                    yesterday=yesterday,
                    funds_available=stringify_number(wallet()),
                    profit_loss=stringify_number(profit_loss(session)))
            else:
                # if the password doesn't match
                flash("Incorrect Username and/or Password")
                return redirect("login")
        else:
            # username doesn't match
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Decorator to render the profile page and display all the info included
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if session["user"]:
        return render_template(
            "profile.html", username=getUsername(session),
            first_name=first_name,
            transactions=transactions,
            transaction_lst=transaction_lst(session),
            stock_aapl=stock_aapl,
            yesterday=yesterday,
            funds_available=stringify_number(wallet()),
            profit_loss=stringify_number(profit_loss(session)))

    return render_template("login")


# Decorator used to render the stock page
@app.route("/stocks")
def stocks():
    return render_template("stocks.html",
                           username=getUsername(session),
                           stock_aapl=stock_aapl,
                           yesterday=yesterday,
                           funds_available=stringify_number(wallet()),
                           profit_loss=stringify_number(profit_loss(session)))


# Decorator used to render the page where the user can purchase stocks
@app.route("/purchase_stocks")
def purchaseStocks():
    return render_template("purchase-stocks.html",
                           username=getUsername(session),
                           stock_aapl=stock_aapl,
                           yesterday=yesterday,
                           funds_available=stringify_number(wallet()),
                           profit_loss=stringify_number(profit_loss(session)))


# Decorator used to process the purchase submitted by the user
# The purchase details are store in MongoDB
@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if request.method == "POST":

        # The purchase will only go forward if the funds available (wallet())
        # is higher that the total purchase amount
        if wallet() >= float(request.form.get("money_amount")):

            # Data taken from the form
            purchase = {
                "purchase_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": request.form.get("stock_amount"),
                "purchase_price": request.form.get("purchase_price"),
                "money_amount": request.form.get("money_amount"),
                "created_by": session["user"]
            }

            mongo.db.transactions.insert_one(purchase)

            # Data inserted into another database in order to have an
            # updated amount of the funds available to the user
            wallet_transaction = {
                "money_amount": -float(request.form.get("money_amount")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

            flash("Purchase Successful")
            return redirect(url_for("stocks"))

        # If the funds available are lower than the total purchase amount
        # nothing will happen and a flash message will be displayed
        else:
            flash("Not enough funds")
            return redirect(url_for("stocks"))


# Decorator to display current open positions, in other words the stock owned
@app.route('/open-positions')
def openPositions():
    return render_template("open-positions.html",
                           username=getUsername(session),
                           transactions=transactions(),
                           transaction_lst=transaction_lst(session),
                           stock_aapl=stock_aapl,
                           yesterday=yesterday,
                           funds_available=stringify_number(wallet()),
                           profit_loss=stringify_number(profit_loss(session)))


# Decorator used to process the sell submitted by the user
# This decorator has an if statement dividing it into three section
# depending if the amount of stocks the user wants to sell is
# smaller, higher or the same has the stocks owned
@app.route("/sell/<position_id>", methods=["GET", "POST"])
def sell(position_id):
    if request.method == "POST":

        # If the user tries to sell less stock that the amount
        # owned the databse has to be updated
        if int(request.form.get(
            "stock_amount_sell")) < int(request.form.get(
                "stocks_owned")):

            # This calculates the amount of stocks remaining to
            # update Monog's database with "update"
            remaining_stock = int(
                request.form.get("stocks_owned")) - int(
                    request.form.get("stock_amount_sell"))

            update = {
                "purchase_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": str(remaining_stock),
                "purchase_price": request.form.get("purchase_price_sell"),
                "money_amount": request.form.get("money_amount_sell"),
                "created_by": session["user"]
            }

            mongo.db.transactions.update(
                {"_id": ObjectId(position_id)}, update)

            # Data inserted into another database in order to have an
            # updated amount of the funds available to the user
            wallet_transaction = {
                "money_amount": float(request.form.get("money_amount_sell")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

            # The sold stocks are then store in closed_positions
            # in order to have history
            sell = {
                "selling_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": request.form.get("stock_amount_sell"),
                "purchase_price": request.form.get("purchase_price_sell"),
                "selling_price": request.form.get("selling_price"),
                "created_by": session["user"]
            }

            mongo.db.closed_positions.insert_one(sell)

            return redirect(url_for('openPositions'))

        # If the user wants to sell the same amount of stocks owned data
        # has to be deleted from the database
        elif int(request.form.get(
            "stock_amount_sell")) == int(request.form.get(
                "stocks_owned")):

            mongo.db.transactions.remove(
                {"_id": ObjectId(position_id)})

            # The sold stocks are then store in closed_positions
            # in order to have history
            sell = {
                "selling_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": request.form.get("stock_amount_sell"),
                "purchase_price": request.form.get("purchase_price_sell"),
                "money_amount": request.form.get("money_amount_sell"),
                "selling_price": request.form.get("selling_price"),
                "stocks_sold": request.form.get("money_amount_sell"),
                "created_by": session["user"]
            }

            mongo.db.closed_positions.insert_one(sell)

            # Data inserted into another database in order to have an
            # updated amount of the funds available to the user
            wallet_transaction = {
                "money_amount": float(request.form.get("money_amount_sell")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

            return redirect(url_for('openPositions'))

        # If the user wants to seel more stocks that the amount owned
        # nothing will happen and a flash message will be displayed
        elif int(request.form.get(
            "stock_amount_sell")) > int(request.form.get(
                "stocks_owned")):
            flash("Insufficient stock owned")

    open_position = mongo.db.transactions.find_one(
        {"_id": ObjectId(position_id)})

    return render_template("sell-stocks.html",
                           username=getUsername(session),
                           stock_aapl=stock_aapl,
                           yesterday=yesterday,
                           funds_available=stringify_number(wallet()),
                           open_position=open_position,
                           profit_loss=stringify_number(profit_loss(session)))


# Decorator used to render a list of closed positions
# The closed positions are stored in MongoDB
@app.route("/closed_positions")
def closedPositions():
    # Retrieve all data from mongoDB's "closed transactions" entries
    closed_positions = mongo.db.closed_positions.find()

    return render_template("closed-positions.html",
                           username=getUsername(session),
                           transactions=transactions(),
                           transaction_lst=transaction_lst(session),
                           stock_aapl=stock_aapl,
                           yesterday=yesterday,
                           funds_available=stringify_number(wallet()),
                           closed_positions=closed_positions,
                           profit_loss=stringify_number(profit_loss(session)))


# Decorator used to add funds to the user's avialable funds
@app.route("/add_funds", methods=["GET", "POST"])
def add_funds():
    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if request.method == "POST":
        # When the user click on the button in the profile page an additional
        # 10k will be added to the available funds
        wallet_transaction = {
            "money_amount": float(10000),
            "created_by": session["user"]
        }

        mongo.db.wallet_transactions.insert_one(wallet_transaction)

        return render_template(
            "profile.html", username=getUsername(session),
            first_name=first_name,
            transactions=transactions,
            transaction_lst=transaction_lst(session),
            stock_aapl=stock_aapl,
            yesterday=yesterday,
            funds_available=stringify_number(wallet()),
            profit_loss=stringify_number(profit_loss(session)))


# Decorator to process logout request
@app.route("/logout")
def logout():
    # remove user's session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
