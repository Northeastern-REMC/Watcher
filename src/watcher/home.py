from flask import Blueprint, render_template

bp = Blueprint("home", __name__, url_prefix="/")

@bp.get("/")
def index():
    return render_template("index.jinja.html")