import os

from flask import Flask, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://pzbwwiazhlckur:9376f8c09de4c84eff9d268156336408ef864152e97e99ce89d49163dc087580@ec2-52-44-166-58.compute-1.amazonaws.com:5432/d8iug83ch38piq")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/signin", methods=["POST"])
def signin():
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE (username = :user AND password = :pw)", {"user": username, "pw": password}).rowcount == 0:
            return render_template("login.html", message="Error")
        else:
            user = db.execute("SELECT * FROM users WHERE (username = :user)", {"user": username})
            review = db.execute("SELECT * FROM reviews WHERE user_id IN (SELECT id FROM users WHERE (username = :user) ORDER BY date DESC)",{"user":username}).fetchone()
            return render_template("user.html", user=user, review=review)

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/signup", methods=["POST"])
def signup():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :user", {"user": username}).rowcount != 0:
        return render_template("registration.html", message="Error")
    else:
        db.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (:username, :password, :firstname, :lastname, :email)",
            {"username": username, "password": password, "firstname": firstname, "lastname": lastname, "email":email})
        db.commit()
        return render_template("success.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/user/book")
def book():
    return render_template("book.html")
