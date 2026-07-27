"""Flask application for the Hyvä aamiainen project."""

import sqlite3

from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import comments
import config
import db
import recipes
import users


app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    """Stop the request if the user is not logged in."""
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    """Show the home page and the list of recipes."""
    all_recipes = recipes.get_recipes()
    return render_template("index.html", recipes=all_recipes)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Show a user profile and their recipes."""
    user = users.get_user(user_id)

    if user is None:
        abort(404)

    user_recipes = users.get_recipes(user_id)

    return render_template(
        "user.html",
        user=user,
        recipes=user_recipes,
    )


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    """Show the image form and save a profile picture."""
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    image_file = request.files.get("image")

    if image_file is None or image_file.filename == "":
        return "Choose an image file.", 400

    if image_file.mimetype != "image/jpeg":
        return "The profile picture must be a JPEG image.", 400

    image = image_file.read()

    if not image:
        return "The image file must not be empty.", 400

    if len(image) > 100 * 1024:
        return "The image file must not be larger than 100 KB.", 400

    users.update_image(session["user_id"], image)

    return redirect("/user/" + str(session["user_id"]))


@app.route("/image/<int:user_id>")
def show_image(user_id):
    """Return a user's profile picture."""
    image = users.get_image(user_id)

    if image is None:
        abort(404)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpeg"

    return response


@app.route("/delete_image", methods=["POST"])
def delete_image():
    """Delete the logged-in user's profile picture."""
    require_login()

    users.delete_image(session["user_id"])

    return redirect("/user/" + str(session["user_id"]))


@app.route("/find_recipe")
def find_recipe():
    """Show the recipe search form and search results."""
    query = request.args.get("query", "").strip()

    breakfast_type_value = request.args.get(
        "breakfast_type",
        "",
    ).strip()

    classification_groups = recipes.get_classification_groups()

    breakfast_type_options = next(
        (
            group["options"]
            for group in classification_groups
            if group["name"] == "Breakfast type"
        ),
        [],
    )

    breakfast_type_id = None

    if breakfast_type_value:
        try:
            breakfast_type_id = int(breakfast_type_value)
        except ValueError:
            return "Invalid breakfast type.", 400

        valid_option_ids = [
            option["id"]
            for option in breakfast_type_options
        ]

        if breakfast_type_id not in valid_option_ids:
            return "Invalid breakfast type.", 400

    if len(query) > 100:
        return "The search query must contain at most 100 characters.", 400

    if query or breakfast_type_id is not None:
        results = recipes.find_recipes(
            query,
            breakfast_type_id,
        )
    else:
        results = []

    return render_template(
        "find_recipe.html",
        query=query,
        results=results,
        breakfast_type_options=breakfast_type_options,
        breakfast_type_id=breakfast_type_id,
    )


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
    """Show the form for adding a new recipe."""
    require_login()

    classification_groups = recipes.get_classification_groups()

    return render_template(
        "new_recipe.html",
        classification_groups=classification_groups,
    )


@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    """Validate and save a new recipe."""
    require_login()

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

    classification_groups = recipes.get_classification_groups()

    allowed_options = {
        group["name"]: {
            str(option["id"])
            for option in group["options"]
        }
        for group in classification_groups
    }

    breakfast_feature_ids = request.form.getlist(
        "breakfast_features"
    )
    breakfast_type_ids = [
        value
        for value in request.form.getlist("breakfast_type")
        if value
    ]
    diet_ids = request.form.getlist("diets")

    if len(breakfast_type_ids) != 1:
        return "Choose exactly one breakfast type.", 400

    if not set(breakfast_feature_ids).issubset(
        allowed_options["Breakfast feature"]
    ):
        return "Invalid breakfast feature.", 400

    if not set(breakfast_type_ids).issubset(
        allowed_options["Breakfast type"]
    ):
        return "Invalid breakfast type.", 400

    if not set(diet_ids).issubset(
        allowed_options["Diet"]
    ):
        return "Invalid diet option.", 400

    selected_values = (
        breakfast_feature_ids
        + breakfast_type_ids
        + diet_ids
    )

    selected_option_ids = [
        int(value)
        for value in dict.fromkeys(selected_values)
    ]

    recipe_id = recipes.add_recipe(
        title,
        ingredients,
        instructions,
        preparation_time,
        user_id,
        selected_option_ids,
    )

    return redirect("/recipe/" + str(recipe_id))


@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    """Show one recipe."""
    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    classifications = recipes.get_classifications(recipe_id)
    recipe_comments = comments.get_comments(recipe_id)
    review_summary = comments.get_review_summary(recipe_id)

    return render_template(
    "recipe.html",
    recipe=recipe,
    classifications=classifications,
    comments=recipe_comments,
    review_summary=review_summary,
    )


@app.route(
    "/recipe/<int:recipe_id>/comment",
    methods=["POST"],
)
def add_comment(recipe_id):
    """Add a comment and rating to a recipe."""
    require_login()

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        abort(404)

    comment_text = request.form.get(
        "comment_text",
        "",
    ).strip()

    if not comment_text:
        return "The comment must not be empty.", 400

    if len(comment_text) > 1000:
        return "The comment is too long.", 400

    rating_value = request.form.get("rating", "")

    try:
        rating = int(rating_value)
    except ValueError:
        return "Choose a rating from 1 to 5.", 400

    if rating < 1 or rating > 5:
        return "Choose a rating from 1 to 5.", 400

    comments.add_comment(
        recipe_id,
        session["user_id"],
        comment_text,
        rating,
    )

    return redirect("/recipe/" + str(recipe_id))


@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    """Show the form for editing a recipe."""
    require_login()

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    if recipe["user_id"] != session["user_id"]:
        return "You are not allowed to edit this recipe.", 403

    classification_groups = recipes.get_classification_groups()
    selected_option_ids = recipes.get_classification_option_ids(
        recipe_id
    )

    return render_template(
    "edit_recipe.html",
    recipe=recipe,
    classification_groups=classification_groups,
    selected_option_ids=selected_option_ids,
    )


@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    """Validate and update an existing recipe."""
    require_login()

    try:
        recipe_id = int(request.form["recipe_id"])
        preparation_time = int(request.form["preparation_time"])
    except ValueError:
        return "Invalid recipe id or preparation time.", 400

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    if recipe["user_id"] != session["user_id"]:
        return "You are not allowed to edit this recipe.", 403

    title = request.form["title"].strip()
    ingredients = request.form["ingredients"].strip()
    instructions = request.form["instructions"].strip()

    if not title or len(title) > 100:
        return "The title must contain 1–100 characters.", 400

    if not ingredients or len(ingredients) > 5000:
        return "Ingredients must contain 1–5000 characters.", 400

    if not instructions or len(instructions) > 5000:
        return "Instructions must contain 1–5000 characters.", 400

    if preparation_time <= 0:
        return "Preparation time must be greater than zero.", 400

    classification_groups = recipes.get_classification_groups()

    allowed_options = {
        group["name"]: {
            str(option["id"])
            for option in group["options"]
        }
        for group in classification_groups
    }

    breakfast_feature_ids = request.form.getlist(
        "breakfast_features"
    )

    breakfast_type_ids = [
        value
        for value in request.form.getlist("breakfast_type")
        if value
    ]

    diet_ids = request.form.getlist("diets")

    if len(breakfast_type_ids) != 1:
        return "Choose exactly one breakfast type.", 400

    if not set(breakfast_feature_ids).issubset(
        allowed_options["Breakfast feature"]
    ):
        return "Invalid breakfast feature.", 400

    if not set(breakfast_type_ids).issubset(
        allowed_options["Breakfast type"]
    ):
        return "Invalid breakfast type.", 400

    if not set(diet_ids).issubset(
        allowed_options["Diet"]
    ):
        return "Invalid diet option.", 400

    selected_values = (
        breakfast_feature_ids
        + breakfast_type_ids
        + diet_ids
    )

    selected_option_ids = [
        int(value)
        for value in dict.fromkeys(selected_values)
    ]

    recipes.update_recipe(
        recipe_id,
        title,
        ingredients,
        instructions,
        preparation_time,
        selected_option_ids,
    )

    return redirect("/recipe/" + str(recipe_id))


@app.route(
    "/remove_recipe/<int:recipe_id>",
    methods=["GET", "POST"],
)
def remove_recipe(recipe_id):
    """Show a confirmation page or delete a recipe."""
    require_login()

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    if recipe["user_id"] != session["user_id"]:
        return "You are not allowed to delete this recipe.", 403

    if request.method == "GET":
        return render_template(
            "remove_recipe.html",
            recipe=recipe,
        )

    if "remove" in request.form:
        recipes.delete_recipe(recipe_id)
        return redirect("/")

    if "back" in request.form:
        return redirect("/recipe/" + str(recipe_id))

    return "Invalid action.", 400