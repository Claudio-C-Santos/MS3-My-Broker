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
from common import yesterday
from common import getUsername
from common import wallet
from common import transactions
from common import transaction_lst
from common import stringify_number
from common import stock_aapl

# instancing Flask
app = Flask(__name__)

# instancing Alpha Advantage API in order to retrieve quotes
app_alpha = TimeSeries("Alpha_Advantage_key")

# instancing access to MongoDB database
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Retrieve all data from mongoDB's "transactions" entries
        transactions = mongo.db.transactions.find()

        # Object where each transaction is appended to from the for loop
        transaction_lst = []

        for items in transactions:
            transaction_lst.append(items)

        profit_loss_lst = []

        for item in transaction_lst:
            profit_loss_lst.append(
                round(((float(stock_aapl[0][yesterday]['4. close']) -
                float(item['purchase_price'])) *
                int(item['stock_amount'])), 2))

        # check if username already exists
        existing_user = mongo.db.users.find_one(
                        {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()

        first_name = mongo.db.users.find_one(
            {"username": session["user"]})["first_name"]

        return render_template(
            "profile.html",
            username=session["user"],
            first_name=first_name,
            transactions=transactions,
            transaction_lst=transaction_lst,
            stock_aapl=stock_aapl,
            yesterday=yesterday,
            funds_available=stringify_number(wallet()),
            profit_loss_lst=profit_loss_lst)

    return render_template("register.html")


@app.route("/login", methods={"GET", "POST"})
def login():
    if request.method == "POST":
        # check if username is in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # confirm password
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    first_name = mongo.db.users.find_one(
                        {"username": session["user"]})["first_name"]
                    # return template with username,
                    # first_name, transactions and stock
                    # The last two are from API.
                    return render_template(
                        "profile.html", 
                        username=session["user"],
                        first_name=first_name,
                        transactions=transactions(),
                        transaction_lst=transaction_lst(session),
                        stock_aapl=stock_aapl,
                        yesterday=yesterday,
                        funds_available=stringify_number(wallet()))
            else:
                # if the password doesn't match
                flash("Incorrect Username and/or Password")
                return redirect("login")
        else:
            # username doesn't match
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
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

    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if session["user"]:
        return render_template(
            "profile.html", username=getUsername(session),
            first_name=first_name,
            transactions=transactions,
            transaction_lst=transaction_lst,
            stock_aapl=stock_aapl,
            yesterday=yesterday,
            funds_available=stringify_number(wallet()))

    return render_template("login")


@app.route("/stocks")
def stocks():
    return render_template("stocks.html",
                            username=getUsername(session),
                            stock_aapl=stock_aapl,
                            yesterday=yesterday,
                            funds_available=stringify_number(wallet()))


@app.route("/purchase_stocks")
def purchaseStocks():
    return render_template("purchase-stocks.html",
                            username=getUsername(session),
                            stock_aapl=stock_aapl,
                            yesterday=yesterday,
                            funds_available=stringify_number(wallet()))


@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if request.method == "POST":
        if wallet() >= float(request.form.get("money_amount")):
            purchase = {
                "purchase_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": request.form.get("stock_amount"),
                "purchase_price": request.form.get("purchase_price"),
                "money_amount": request.form.get("money_amount"),
                "created_by": session["user"]
            }

            mongo.db.transactions.insert_one(purchase)

            # Update funds available
            wallet_transaction = {
                "money_amount": -float(request.form.get("money_amount")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

            flash("Purchase Successful")
            return redirect(url_for("stocks"))
        else:
            flash("Not enough funds")
            return redirect(url_for("stocks"))


@app.route('/open-positions')
def openPositions():
    return render_template("open-positions.html",
                            username=getUsername(session),
                            transactions=transactions(),
                            transaction_lst=transaction_lst(session),
                            stock_aapl=stock_aapl,
                            yesterday=yesterday,
                            funds_available=stringify_number(wallet()))


@app.route("/sell/<position_id>", methods=["GET", "POST"])
def sell(position_id):
    if request.method == "POST":
        if int(request.form.get(
            "stock_amount_sell")) < int(request.form.get(
                "stocks_owned")):

            remaining_stock = int(
                request.form.get("stocks_owned")) - int(
                    request.form.get("stock_amount_sell"))

            update = {
                "selling_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": str(remaining_stock),
                "purchase_price": request.form.get("purchase_price_sell"),
                "money_amount": request.form.get("money_amount_sell"),
                "created_by": session["user"]
            }

            mongo.db.transactions.update(
                {"_id": ObjectId(position_id)}, update)

            # Update funds available
            wallet_transaction = {
                "money_amount": float(request.form.get("money_amount_sell")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

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

            funds_used_adj = float(item['money_amount']) - float(request.form.get("money_amount_sell"))

            sell = {
                "selling_date": yesterday,
                "ticker": request.form.get('ticker'),
                "stock_amount": str(remaining_stock),
                "purchase_price": request.form.get("purchase_price_sell"),
                "money_amount": str(funds_used_adj),
                "selling_price": request.form.get("selling_price"),
                "created_by": session["user"]
            }

            mongo.db.closed_positions.insert_one(sell)

            return redirect(url_for('openPositions'))

        elif int(request.form.get(
            "stock_amount_sell")) == int(request.form.get(
                "stocks_owned")):

            mongo.db.transactions.remove(
                {"_id": ObjectId(position_id)})

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

            # Update funds available
            wallet_transaction = {
                "money_amount": float(request.form.get("money_amount_sell")),
                "created_by": session["user"]
            }

            mongo.db.wallet_transactions.insert_one(wallet_transaction)

            return redirect(url_for('openPositions'))

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
                            open_position=open_position)


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
                            closed_positions=closed_positions)


@app.route("/logout")
def logout():
    # remove user's session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ ==   "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
