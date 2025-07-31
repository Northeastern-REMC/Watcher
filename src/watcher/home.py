from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import text
from datetime import datetime, timedelta
from collections import OrderedDict

from watcher.db import db
from watcher.constants import IGNITION_EPOCH, NREMC_TIMEZONE
from watcher.forms import SubmissionForm

bp = Blueprint("home", __name__, url_prefix="/")

def pop(form):
    current_date = datetime.now(NREMC_TIMEZONE)
    dates = OrderedDict()
    cursor = IGNITION_EPOCH.replace(day=1)
    while cursor <= current_date:
        month_str = cursor.strftime("%m-%Y")
        dates[month_str] = None
        # Go to the first day of the next month
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)
    
    form.date_select.choices = [(d, d) for d in dates]


@bp.get("/")
def index():
    current_date = datetime.now(NREMC_TIMEZONE)
    dates = OrderedDict(
        ((IGNITION_EPOCH + timedelta(_)).strftime(r"%m-%Y"), None)
        for _ in range((current_date - IGNITION_EPOCH).days)
    ).keys()
    form = SubmissionForm()
    pop(form)

    return render_template("index.jinja.html", form=form)


@bp.post("/")
def get_info():
    form = SubmissionForm(request.form)
    pop(form)
    
    if form.validate():
        station = form.station_select.data
        ess = form.ess_select.data
        date = form.date_select.data
        error_type = form.type_select.data
        return redirect(url_for("home.index"))
    else:
        return "FUCK YOU", 400
