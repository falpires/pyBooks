import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET")
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set up the Bcrypt for hashing

bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    ''' This route is to register users, GET returns the form, POST registers in the database '''

    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("passwd")
        confirm = request.form.get("confirm")

        # Check for values missing
        if not username or not password:
            return "Input a valid username and/or password"
        # Check if passwords match
        if confirm != password:
            return "Passwords do not match"

        # Check if username is not already in use
        if db.execute("SELECT username FROM users WHERE username = :username",
                            {"username": username}).rowcount >= 1:
            return render_template("register.html", message="Username already in use")

        # Generate password hash for storing the password
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        
        # Execute DB Query to insert into users
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
                   {"username":username, "password":pw_hash})
        db.commit()
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("passwd")

        # Check for values missing
        if not username or not password:
            return "Input a valid username and/or password"
        
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()
        if not user:
            return "Some error has ocurred"
        if bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = user["id"] 
            return "Logged in?"
        return "Password and/or user not match"
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    if request.method == "POST":
        session.pop("user_id", None)
        return redirect(url_for("login"))
    else:
        return render_template("logout.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    '''
    Later i want it to be only "GET" method, as there is no sensitive information to be placed in this form
    '''
    if request.method == "POST":
        filter_by = request.form.get("filter")
        if not filter_by:
            return "Please specify a filter"

        value = request.form.get("search")
        if not value:
            return "Please specify a value" 
        
        '''
        My dream was to actually use the WHERE clause by placing dynamic values, but it doesn't turned well, 
        because the sqlalchemy lib puts the WHERE filter with '' in it, and it causes the Query to not return anything...
        In this case i will use if's and elif's... Maybe i could use jinja2 to render the query, but will test it later.
        Or i'll not test it at all, i'm crazy to use the ORM!
        '''
        if filter_by == "author":
            QUERY = "SELECT * FROM books WHERE author LIKE :value"
        elif filter_by == "title":
            QUERY = "SELECT * FROM books WHERE title LIKE :value"
        elif filter_by == "isbn":
            QUERY = "SELECT * FROM books WHERE isbn LIKE :value"

        # It turned out that i had to do this for LIKE clause... I don't like it at all...
        books = db.execute(QUERY, {"value": "%" + value + "%"}).fetchall()

        if not books:
            return render_template("search.html", error="Your search has not returned any results... Try again!")
        
        return render_template("search.html", books=books)
    else:
        return render_template("search.html")

@app.route("/book/<int:id>")
@login_required
def book(id):
    '''
    Page showing the detais of a book by it's ID
    '''

    book = db.execute("SELECT title, author, year, isbn FROM books WHERE id = :id", {"id":id}).fetchone()

    reviews = db.execute("SELECT rating, review FROM reviews WHERE book_id = :id", {"id":id}).fetchall()

    return render_template("book.html", book=book, reviews=reviews)