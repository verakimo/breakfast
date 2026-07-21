from flask import Flask
from flask import render_template
import db

app = Flask(__name__)

@app.route("/")
def index():
    groups = db.query(
        "SELECT id, name "
        "FROM classification_groups "
        "ORDER BY id"
    )
    return render_template("index.html", groups=groups)

