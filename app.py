"""Flask application for the Hyvä aamiainen project."""

import sqlite3

from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config
import db
import recipes


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


@app.route("/new_recipe")
def new_recipe():
    """Show the form for adding a recipe."""
    if "user_id" not in session:
        return redirect("/")

    return render_template("new_recipe.html")


@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    """Validate and save a new recipe."""
    if "user_id" not in session:
        return "You must be logged in to add a recipe.", 401

    title = request.form["title"].strip()
    ingredients = request.form["ingredients"].strip()
    instructions = request.form["instructions"].strip()

    try:
        preparation_time = int(request.form["preparation_time"])
    except ValueError:
        return "Preparation time must be a whole number.", 400

    if not title or len(title) > 100:
        return "The title must contain 1–100 characters.", 400

    if not ingredients or len(ingredients) > 5000:
        return "Ingredients must contain 1–5000 characters.", 400

    if not instructions or len(instructions) > 5000:
        return "Instructions must contain 1–5000 characters.", 400

    if preparation_time <= 0:
        return "Preparation time must be greater than zero.", 400

    user_id = session["user_id"]

    recipe_id = recipes.add_recipe(
        title,
        ingredients,
        instructions,
        preparation_time,
        user_id,
    )

    return redirect("/recipe/" + str(recipe_id))


@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    """Show one recipe."""
    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    return render_template("recipe.html", recipe=recipe)