import os
import requests

from flask import Flask, render_template, request, session, jsonify, redirect
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
user = None
review = None

@app.route("/")
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route("/account/<int:status>", methods=["POST"])
def account(status):
    if status==0:
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE (username = :user AND password = :pw)", {"user": username, "pw": password}).rowcount == 0:
            return render_template("login.html", message="Error")
        else:
            user = db.execute("SELECT * FROM users WHERE (username = :user)", {"user": username})
            review = db.execute("SELECT * FROM reviews WHERE user_id IN (SELECT id FROM users WHERE (username = :user) ORDER BY date DESC)",{"user":username}).fetchone()
            return render_template("user.html", review=review, status=0, user=user)
    elif status==1:
        search = request.form.get("search")
        text = '%' + search.capitalize() + '%'
        books = db.execute("SELECT * FROM books WHERE ((ISBN LIKE :text) OR (title LIKE :text) OR (author LIKE :text))",{"text": text}).fetchall()
        return render_template("user.html", status=1, books=books, review=None)

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

@app.route("/account/book/<string:ISBN>")
def book(ISBN):
    book = db.execute("SELECT * FROM books WHERE ISBN = :isbn", {"isbn": ISBN}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :isbn", {"isbn": ISBN}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "bTGMYyGXxoJ4dyQANv0A", "isbns": ISBN})
    book_gr = res.json()
    good_reads = book_gr['books']
    gr = good_reads[0]
    stars = int(gr['average_rating'][0])
    return render_template("book.html", book=book, reviews=reviews, good_reads=good_reads[0], stars=stars)

@app.route("/api/<string:ISBN>")
def book_api(ISBN):

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE ISBN = :isbn", {"isbn": ISBN}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 422

    return jsonify({
            "ISBN": book.isbn,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "stars": book.stars,
            "review_count": book.review_count
        })
