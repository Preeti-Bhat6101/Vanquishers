from flask import Flask, flash, redirect, request, render_template, session
from flask_session import Session
from  flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os
import sqlite3
from datetime import datetime

DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def homepage():
    return "hi"






@app.route("/login", methods=["GET", "POST"])
def login():
    
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("Password must be same")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", (username, hash))
        except ValueError:
            flash("Username already taken")
    
    else:
        return render_template("signup.html")
    
    return redirect("/login")
            







