import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from alpha_vantage.timeseries import TimeSeries
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app_alpha = TimeSeries("Alpha_Advantage_key")

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("Flask_Secret_Key")

# FUNDS AVAILABLE
# funds_available = 100

mongo = PyMongo(app)


# Global Variables
# Retrieve all data from mongoDB's "transactions" entries
TRANSACTIONS = mongo.db.transactions.find()
# Retrieve stock info from Alpha Advantage API
STOCK = app_alpha.get_daily_adjusted("IBM")


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
            transactions=TRANSACTIONS)
    return render_template("register.html")


@app.route("/login", methods={"GET", "POST"})
def login():
    # Retrieve all data from mongoDB's "transactions" entries
    TRANSACTIONS = mongo.db.transactions.find()

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
                        transactions=TRANSACTIONS)

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
    TRANSACTIONS = mongo.db.transactions.find()

    # use the sessions's data from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    first_name = mongo.db.users.find_one(
        {"username": session["user"]})["first_name"]

    if session["user"]:
        return render_template(
            "profile.html", username=username,
            first_name=first_name,
            transactions=TRANSACTIONS)

    return render_template("login")


@app.route("/logout")
def logout():
    # remove user's session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


'''
@app.route("/get_transactions")
def get_transactions():
    transactions = mongo.db.transactions.find()
    stock = app_alpha.get_daily_adjusted("IBM")
    return render_template(
                            "profile.html",
                            transactions=TRANSACTIONS, stock=STOCK)


# FUNDS AVAILABLE

@app.route("profile/<funds_available>")
def funds_available(funds_available):
    funds_available = funds_available

    return render_template("profile.html", funds_available=funds_available)
'''


if __name__ ==   "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
