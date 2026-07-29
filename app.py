"""Flask application for the Hyvä aamiainen project."""

import secrets
import sqlite3
import markupsafe

from flask import Flask
from flask import abort, flash, make_response, redirect, render_template, request, session
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


def check_csrf():
    """Stop the request if the CSRF token is missing or invalid."""
    form_token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")

    if not form_token or not session_token:
        abort(403)

    if form_token != session_token:
        abort(403)


def get_safe_next_page():
    """Return a safe internal page for redirecting the user."""
    next_page = (
        request.form.get("next_page")
        or request.args.get("next_page")
        or "/"
    )

    if (
        not next_page.startswith("/")
        or next_page.startswith("//")
        or "\\" in next_page
    ):
        return "/"

    return next_page


def ensure_csrf_token():
    """Create a CSRF token if the session does not have one."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


@app.before_request
def create_csrf_token():
    """Ensure that every session has a CSRF token."""
    ensure_csrf_token()


@app.template_filter()
def show_lines(content):
    """Show line breaks in user-provided text safely."""
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br>")
    return markupsafe.Markup(content)


@app.route("/")
def index():
    """Show the home page and the list of recipes."""
    ensure_csrf_token()
    all_recipes = recipes.get_recipes()
    return render_template(
        "index.html",
        recipes=all_recipes,
        filled_login={},
    )


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

    check_csrf()

    image_file = request.files.get("image")

    if image_file is None or image_file.filename == "":
        flash("Choose an image file.")
        return redirect("/add_image")

    if image_file.mimetype != "image/jpeg":
        flash("The profile picture must be a JPEG image.")
        return redirect("/add_image")

    image = image_file.read()

    if not image:
        flash("The image file must not be empty.")
        return redirect("/add_image")

    if len(image) > 100 * 1024:
        flash("The image file must not be larger than 100 KB.")
        return redirect("/add_image")

    users.update_image(session["user_id"], image)
    flash("Profile picture updated successfully.")

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
    check_csrf()

    users.delete_image(session["user_id"])
    flash("Profile picture deleted successfully.")

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
        flash("The search query must contain at most 100 characters.")
        return render_template(
            "find_recipe.html",
            query=query,
            breakfast_type_options=breakfast_type_options,
            breakfast_type_id=breakfast_type_id,
            results=[],
        ), 400

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
    ensure_csrf_token()
    return render_template(
        "register.html",
        filled={},
    )


@app.route("/create", methods=["POST"])
def create():
    """Create a new user account."""
    check_csrf()

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not 3 <= len(username) <= 30:
        flash("The username must contain 3–30 characters.")
        return render_template(
            "register.html",
            filled={"username": username},
        ), 400

    if not 8 <= len(password1) <= 100:
        flash("The password must contain 8–100 characters.")
        return render_template(
            "register.html",
            filled={"username": username},
        ), 400

    if password1 != password2:
        flash("The passwords do not match.")
        return render_template(
            "register.html",
            filled={"username": username},
        ), 400

    password_hash = generate_password_hash(password1)

    try:
        sql = """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("The username is already taken.")
        return render_template(
            "register.html",
            filled={"username": username},
        ), 409

    flash("Account created successfully. You can now log in.")
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    """Log a user in when the username and password are correct."""
    check_csrf()
    username = request.form["username"].strip()
    password = request.form["password"]

    sql = """
        SELECT id, username, password_hash
        FROM users
        WHERE username = ?
    """
    rows = db.query(sql, [username])

    if not rows:
        flash("Invalid username or password.")
        all_recipes = recipes.get_recipes()
        return render_template(
            "index.html",
            recipes=all_recipes,
            filled_login={"username": username},
        ), 401

    user = rows[0]

    if not check_password_hash(user["password_hash"], password):
        flash("Invalid username or password.")
        all_recipes = recipes.get_recipes()
        return render_template(
            "index.html",
            recipes=all_recipes,
            filled_login={"username": username},
        ), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["csrf_token"] = secrets.token_hex(16)

    flash("Logged in successfully.")
    return redirect("/")


@app.route("/logout", methods=["POST"])
def logout():
    """Log the current user out."""
    require_login()
    check_csrf()

    session.clear()
    flash("Logged out successfully.")
    return redirect("/")


def render_new_recipe_form(filled=None):
    """Render the new recipe form with entered values."""
    if filled is None:
        filled = {
            "title": "",
            "ingredients": "",
            "instructions": "",
            "preparation_time": "",
            "breakfast_features": [],
            "breakfast_type": "",
            "diets": [],
        }

    classification_groups = recipes.get_classification_groups()

    return render_template(
        "new_recipe.html",
        classification_groups=classification_groups,
        filled=filled,
    )


@app.route("/new_recipe")
def new_recipe():
    """Show the form for adding a new recipe."""
    require_login()
    return render_new_recipe_form()


@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    """Validate and save a new recipe."""
    require_login()
    check_csrf()

    title = request.form.get("title", "").strip()
    ingredients = request.form.get("ingredients", "").strip()
    instructions = request.form.get("instructions", "").strip()

    preparation_time_value = request.form.get("preparation_time", "")

    breakfast_feature_ids = request.form.getlist(
        "breakfast_features"
    )
    breakfast_type_ids = [
        value
        for value in request.form.getlist("breakfast_type")
        if value
    ]
    diet_ids = request.form.getlist("diets")

    filled = {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "preparation_time": preparation_time_value,
        "breakfast_features": breakfast_feature_ids,
        "breakfast_type": (
            breakfast_type_ids[0]
            if len(breakfast_type_ids) == 1
            else ""
        ),
        "diets": diet_ids,
    }

    try:
        preparation_time = int(preparation_time_value)
    except ValueError:
        flash("Preparation time must be a whole number.")
        return render_new_recipe_form(filled), 400

    if not title or len(title) > 100:
        flash("The title must contain 1–100 characters.")
        return render_new_recipe_form(filled), 400

    if not ingredients or len(ingredients) > 5000:
        flash("Ingredients must contain 1–5000 characters.")
        return render_new_recipe_form(filled), 400

    if not instructions or len(instructions) > 5000:
        flash("Instructions must contain 1–5000 characters.")
        return render_new_recipe_form(filled), 400

    if preparation_time <= 0:
        flash("Preparation time must be greater than zero.")
        return render_new_recipe_form(filled), 400

    user_id = session["user_id"]

    classification_groups = recipes.get_classification_groups()

    allowed_options = {
        group["name"]: {
            str(option["id"])
            for option in group["options"]
        }
        for group in classification_groups
    }

    if len(breakfast_type_ids) != 1:
        flash("Choose exactly one breakfast type.")
        return render_new_recipe_form(filled), 400

    if not set(breakfast_feature_ids).issubset(
        allowed_options["Breakfast feature"]
    ):
        flash("Invalid breakfast feature.")
        return render_new_recipe_form(filled), 400

    if not set(breakfast_type_ids).issubset(
        allowed_options["Breakfast type"]
    ):
        flash("Invalid breakfast type.")
        return render_new_recipe_form(filled), 400

    if not set(diet_ids).issubset(
        allowed_options["Diet"]
    ):
        flash("Invalid diet option.")
        return render_new_recipe_form(filled), 400

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

    flash("Recipe created successfully.")
    return redirect("/recipe/" + str(recipe_id))


def render_recipe_page(
    recipe_id,
    filled_review=None,
    next_page=None,
):
    """Render a recipe page with review form values."""
    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        abort(404)

    if filled_review is None:
        filled_review = {
            "comment_text": "",
            "rating": "",
        }

    if next_page is None:
        next_page = get_safe_next_page()

    classifications = recipes.get_classifications(recipe_id)
    recipe_comments = comments.get_comments(recipe_id)
    review_summary = comments.get_review_summary(recipe_id)

    return render_template(
        "recipe.html",
        recipe=recipe,
        classifications=classifications,
        comments=recipe_comments,
        review_summary=review_summary,
        filled_review=filled_review,
        next_page=next_page,
    )


@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    """Show one recipe."""
    return render_recipe_page(recipe_id)


@app.route(
    "/recipe/<int:recipe_id>/comment",
    methods=["POST"],
)
def add_comment(recipe_id):
    """Add a comment and rating to a recipe."""
    require_login()
    check_csrf()

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        abort(404)

    comment_text = request.form.get(
        "comment_text",
        "",
    ).strip()
    rating_value = request.form.get("rating", "")

    filled_review = {
        "comment_text": comment_text,
        "rating": rating_value,
    }

    if not comment_text:
        flash("The comment must not be empty.")
        return render_recipe_page(
            recipe_id,
            filled_review,
        ), 400

    if len(comment_text) > 1000:
        flash("The comment must not contain more than 1000 characters.")
        return render_recipe_page(
            recipe_id,
            filled_review,
        ), 400

    try:
        rating = int(rating_value)
    except ValueError:
        flash("Choose a rating from 1 to 5.")
        return render_recipe_page(
            recipe_id,
            filled_review,
        ), 400

    if rating < 1 or rating > 5:
        flash("Choose a rating from 1 to 5.")
        return render_recipe_page(
            recipe_id,
            filled_review,
        ), 400

    comments.add_comment(
        recipe_id,
        session["user_id"],
        comment_text,
        rating,
    )

    flash("Review added successfully.")
    return redirect("/recipe/" + str(recipe_id))


def render_edit_recipe_form(
    recipe,
    filled=None,
    selected_option_ids=None,
):
    """Render the edit recipe form with entered values."""
    if filled is None:
        filled = {
            "title": recipe["title"],
            "ingredients": recipe["ingredients"],
            "instructions": recipe["instructions"],
            "preparation_time": recipe["preparation_time"],
        }

    if selected_option_ids is None:
        selected_option_ids = [
            str(option_id)
            for option_id in recipes.get_classification_option_ids(
                recipe["id"]
            )
        ]

    classification_groups = recipes.get_classification_groups()

    return render_template(
        "edit_recipe.html",
        recipe=recipe,
        filled=filled,
        classification_groups=classification_groups,
        selected_option_ids=selected_option_ids,
    )


@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    """Show the form for editing a recipe."""
    require_login()

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    if recipe["user_id"] != session["user_id"]:
        return "You are not allowed to edit this recipe.", 403

    return render_edit_recipe_form(recipe)


@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    """Validate and update an existing recipe."""
    require_login()
    check_csrf()

    recipe_id_value = request.form.get("recipe_id", "")

    try:
        recipe_id = int(recipe_id_value)
    except ValueError:
        return "Invalid recipe id.", 400

    recipe = recipes.get_recipe(recipe_id)

    if recipe is None:
        return "Recipe not found.", 404

    if recipe["user_id"] != session["user_id"]:
        return "You are not allowed to edit this recipe.", 403

    title = request.form.get("title", "").strip()
    ingredients = request.form.get("ingredients", "").strip()
    instructions = request.form.get("instructions", "").strip()
    preparation_time_value = request.form.get(
        "preparation_time",
        "",
    )

    breakfast_feature_ids = request.form.getlist(
        "breakfast_features"
    )
    breakfast_type_ids = [
        value
        for value in request.form.getlist("breakfast_type")
        if value
    ]
    diet_ids = request.form.getlist("diets")

    filled = {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "preparation_time": preparation_time_value,
    }

    selected_values = (
        breakfast_feature_ids
        + breakfast_type_ids
        + diet_ids
    )

    selected_option_ids = list(
        dict.fromkeys(selected_values)
    )

    try:
        preparation_time = int(preparation_time_value)
    except ValueError:
        flash("Preparation time must be a whole number.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not title or len(title) > 100:
        flash("The title must contain 1–100 characters.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not ingredients or len(ingredients) > 5000:
        flash("Ingredients must contain 1–5000 characters.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not instructions or len(instructions) > 5000:
        flash("Instructions must contain 1–5000 characters.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if preparation_time <= 0:
        flash("Preparation time must be greater than zero.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    classification_groups = recipes.get_classification_groups()

    allowed_options = {
        group["name"]: {
            str(option["id"])
            for option in group["options"]
        }
        for group in classification_groups
    }

    if len(breakfast_type_ids) != 1:
        flash("Choose exactly one breakfast type.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not set(breakfast_feature_ids).issubset(
        allowed_options["Breakfast feature"]
    ):
        flash("Invalid breakfast feature.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not set(breakfast_type_ids).issubset(
        allowed_options["Breakfast type"]
    ):
        flash("Invalid breakfast type.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    if not set(diet_ids).issubset(
        allowed_options["Diet"]
    ):
        flash("Invalid diet option.")
        return render_edit_recipe_form(
            recipe,
            filled,
            selected_option_ids,
        ), 400

    validated_option_ids = [
        int(value)
        for value in selected_option_ids
    ]

    recipes.update_recipe(
        recipe_id,
        title,
        ingredients,
        instructions,
        preparation_time,
        validated_option_ids,
    )

    flash("Recipe updated successfully.")
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

    next_page = get_safe_next_page()

    if request.method == "GET":
        return render_template(
            "remove_recipe.html",
            recipe=recipe,
            next_page=next_page,
        )

    check_csrf()

    if "remove" in request.form:
        recipes.delete_recipe(recipe_id)
        flash("Recipe deleted successfully.")
        return redirect(next_page)

    return "Invalid action.", 400