from flask import Blueprint, render_template
from sqlalchemy import text
from datetime import datetime, timedelta
from collections import OrderedDict

from watcher.db import db
from watcher.constants import IGNITION_EPOCH, NREMC_TIMEZONE

bp = Blueprint("home", __name__, url_prefix="/")


@bp.get("/")
def index():
    current_date = datetime.now(NREMC_TIMEZONE)
    dates = OrderedDict(
        ((IGNITION_EPOCH + timedelta(_)).strftime(r"%m-%Y"), None)
        for _ in range((current_date - IGNITION_EPOCH).days)
    ).keys()

    return render_template("index.jinja.html", dates=dates)
