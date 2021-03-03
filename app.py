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

# instancing Flask
app = Flask(__name__)


# instancing Alpha Advantage API in order to retrieve quotes
app_alpha = TimeSeries("Alpha_Advantage_key")
# Retrieve stock info from Alpha Advantage API
stock_aapl = app_alpha.get_daily_adjusted("AAPL")

# instancing access to MongoDB database
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

mongo = PyMongo(app)

# Retrieve all data from mongoDB's "transactions" entries
transactions = mongo.db.transactions.find()


# Retrieve all data from mongoDB's "wallet_transactions" entries
wallet_transactions = mongo.db.wallet_transactions.find()

wallet_statements = []

for statements in wallet_transactions:
    wallet_statements.append(statements['money_amount'])

initial_funds = 10000
funds_available = initial_funds + sum(wallet_statements)
funds = format(funds_available, ",")


# Yesterday Selector
dayValidator = datetime.now().strftime('%w')

if dayValidator == '0':
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
elif dayValidator == '1':
    yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
else:
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


# Object where each transaction is appended to from the for loop
transaction_lst = []

for items in transactions:
    transaction_lst.append(items)

profit_loss_lst = []

for item in transaction_lst:
    profit_loss_lst.append(
        round(((float(item['purchase_price']) - float(stock_aapl[0][yesterday]['4. close'])) * int(item['stock_amount'])), 2))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
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
            transactions=transactions)
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
                        transactions=transactions,
                        transaction_lst=transaction_lst,
                        stock_aapl=stock_aapl,
                        yesterday=yesterday,
                        funds_available=funds,
                        profit_loss_lst=profit_loss_lst)
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
    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if session["user"]:
        return render_template(
            "profile.html", username=username,
            first_name=first_name,
            transactions=transactions,
            transaction_lst=transaction_lst,
            stock_aapl=stock_aapl,
            yesterday=yesterday,
            funds_available=funds_available,
            profit_loss_lst=profit_loss_lst,
            wallet_statements=wallet_statements)

    return render_template("login")


@app.route("/stocks")
def stocks():
    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    return render_template("stocks.html",
                            username=username,
                            stock_aapl=stock_aapl,
                            yesterday=yesterday,
                            funds_available=funds_available,
                            profit_loss_lst=profit_loss_lst)


@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    if request.method == "POST":
        purchase = {
            "purchase_date": yesterday,
            "ticker": request.form.get('ticker'),
            "stock_amount": request.form.get("stock_amount"),
            "purchase_price": request.form.get("purchase_price"),
            "money_amount": request.form.get("money_amount"),
            "purchase_by": session["user"]
        }
        mongo.db.transactions.insert_one(purchase)
        wallet_transaction = {
            "money_amount": -float(request.form.get("money_amount"))
        }
        mongo.db.wallet_transactions.insert_one(wallet_transaction)
        return redirect(url_for("stocks"))


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
