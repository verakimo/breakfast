"""Flask application for the Hyvä aamiainen project."""

import sqlite3

from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db


app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    """Show the home page and the login form."""
    return render_template("index.html")


@app.route("/register")
def register():
    """Show the registration form."""
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    """Create a new user account."""
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not 3 <= len(username) <= 30:
        return "The username must contain 3–30 characters.", 400

    if not 8 <= len(password1) <= 100:
        return "The password must contain 8–100 characters.", 400

    if password1 != password2:
        return "The passwords do not match.", 400

    password_hash = generate_password_hash(password1)

    try:
        sql = """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "The username is already taken.", 409

    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    """Log a user in when the username and password are correct."""
    username = request.form["username"].strip()
    password = request.form["password"]

    sql = """
        SELECT id, username, password_hash
        FROM users
        WHERE username = ?
    """
    rows = db.query(sql, [username])

    if not rows:
        return "Invalid username or password.", 401

    user = rows[0]

    if not check_password_hash(user["password_hash"], password):
        return "Invalid username or password.", 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return redirect("/")


@app.route("/logout")
def logout():
    """Log the current user out."""
    session.clear()
    return redirect("/")
