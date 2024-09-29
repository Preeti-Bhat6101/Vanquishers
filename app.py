from flask import Flask, flash, redirect, request, render_template, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  
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
    db.execute('''
        CREATE TABLE IF NOT EXISTS outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            outfit_name TEXT NOT NULL,
            image_filename TEXT NOT NULL, 
            preference_score INTEGER DEFAULT 0, 
            category TEXT NOT NULL, 
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


init_db()

app.config["SECRET_KEY"] = "hgfhsdhdfhs dfhsefh"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
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
        conn.commit()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid Username or Password", 'error')
            return redirect("/login")

    
        session["user_id"] = rows[0]["id"]
        return redirect("/wardrobe")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            flash("Passwords must match", 'error')
            return redirect("/signup")

        hash = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already taken", 'error')
            return redirect("/signup")
        finally:
            conn.close()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/wardrobe", methods=["GET", "POST"])
def wardrobe():
    if request.method == "POST":
        outfit_name = request.form.get("outfit_name")
        user_id = session["user_id"]
        preference_score = request.form.get("preference_score", 5)
        category = request.form.get("category")
        
        if 'file' not in request.files:
            flash("No file part", 'error')
            return redirect("/wardrobe")
        
        file = request.files['file']
        
        if file.filename == '':
            flash("No selected file", 'error')
            return redirect("/wardrobe")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            
            conn = get_db()
            conn.execute("INSERT INTO outfits (user_id, outfit_name, image_filename, preference_score, category) VALUES (?, ?, ?, ?, ?)",
                         (user_id, outfit_name, filename, preference_score, category))
            conn.commit()
            conn.close()

            flash("Outfit added!", 'success')
            return redirect("/wardrobe")

    
    user_id = session["user_id"]
    conn = get_db()
    outfits = conn.execute("SELECT * FROM outfits WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    return render_template("wardrobe.html", outfits=outfits)

@app.route("/delete_outfit/<int:outfit_id>", methods=["POST"])
def delete_outfit(outfit_id):
    conn = get_db()
    conn.execute("DELETE FROM outfits WHERE id = ?", (outfit_id,))
    conn.commit()
    conn.close()

    flash("Outfit deleted!", 'success')
    return redirect("/wardrobe")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/profile")
def profile():
    user_id = session["user_id"]
    conn = get_db()

    preferred_outfits = conn.execute("SELECT * FROM outfits WHERE user_id = ? ORDER BY preference_score DESC", (user_id,)).fetchall()
    
    least_preferred_outfits = conn.execute("SELECT * FROM outfits WHERE user_id = ? ORDER BY preference_score ASC LIMIT 5", (user_id,)).fetchall()

    conn.close()
    
    return render_template("profile.html", preferred_outfits=preferred_outfits, least_preferred_outfits=least_preferred_outfits)

@app.route("/community")
def community():
    return render_template("community.html")

if __name__ == '__main__':
    app.run(port=8000)
