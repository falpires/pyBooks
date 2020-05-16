import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set up the Bcrypt for hashing

bcrypt = Bcrypt(app)


@app.route("/")
def index():
    return "Project 1: TODO"

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


