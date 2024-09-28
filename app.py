from flask import Flask, flash, redirect, request, render_template, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # To fetch rows as dictionaries
    return conn

def init_db():
    conn = get_db()
    db = conn.cursor()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the application starts
init_db()

app.config["SECRET_KEY"] = "hgfhsdhdfhs dfhsefh"
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
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        conn = get_db()
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        print(rows)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid Username or Password")
            return redirect("/login")

        # Log the user in
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("Passwords must match")
            return redirect("/signup")

        hash = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already taken")
            return redirect("/signup")
        finally:
            conn.close()

        return redirect("/login")

    return render_template("signup.html")

if __name__ == '__main__':
    app.run(debug=True)
