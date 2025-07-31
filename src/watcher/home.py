import io
from flask import Blueprint, redirect, render_template, request, send_file, url_for
from sqlalchemy import text
from datetime import datetime, timedelta
from collections import OrderedDict

from watcher.db import db
from watcher.constants import ALARM_BIT_MAP, FAULT_BIT_MAP, IGNITION_EPOCH, NREMC_TIMEZONE
from watcher.forms import SubmissionForm

import pandas as pd

bp = Blueprint("home", __name__, url_prefix="/")

def get_sub_form():
    current_date = datetime.now(NREMC_TIMEZONE)
    form = SubmissionForm(request.form)
    form.date_select.choices = [(d, d) for d in pd.date_range(IGNITION_EPOCH, current_date, freq="MS").strftime(r"%m-%Y").tolist()]
    return form


@bp.get("/")
def index():
    form = get_sub_form()

    return render_template("index.jinja.html", form=form)

@bp.get("/display")
def display():
    station = request.args.get("station")
    ess = request.args.get("ess")
    error_type = request.args.get("error_type")
    date = request.args.get("date")
    page = request.args.get("page")

    if page is None:
        page = 1
    
    
    tag_path = f"'%nremc/bess/{station}/{ess}/bms/state/{error_type}2%'"
    month, year = date.split("-")

    sql_query = (
        "WITH MatchingTags AS (\n"
        "   SELECT\n"
        "       id as tagid,\n"
        "       tagpath\n"
        "   FROM [dbNREMCHistorianBESSSTS].[dbo].[sqlth_te]\n"
        "   WHERE retired is NULL\n"
        f"     AND tagpath LIKE {tag_path}\n"
        ")\n"
        "SELECT\n"
        "   d.tagid,\n"
        "   t.tagpath,\n"
        "   d.t_stamp,\n"
        "   d.floatvalue,\n"
        "   d.intvalue\n"
        "FROM MatchingTags t\n"
        f"JOIN [dbNREMCHistorianBESSSTS].[dbo].[sqlt_data_2_{year}_{month}] d\n" #! DO NOT DO THIS SHIT THIS IS BAD
        "   ON t.tagid = d.tagid\n"
        "ORDER BY d.t_stamp DESC;"
    )
    df = pd.read_sql(sql_query, db.engine) # type: ignore
    df["station"] = station
    df["type"] = error_type
    df["timestamp"] = pd.to_datetime(df["t_stamp"], unit="ms")
    
    if error_type == "fault":
        for bit, label in FAULT_BIT_MAP.items():
            df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1))
    else:
        for bit, label in ALARM_BIT_MAP.items():
            df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1))
    
    df = df.drop(columns=["t_stamp", "floatvalue", "tagid","tagpath", "intvalue"])
    to_get = int(page)*5
    print(df.values.tolist()[:int(page)-1])
    
    return render_template('display.jinja.html', ll=df.values.tolist()[(int(page)-1)*5:int(page)*5-1])
    


@bp.post("/")
def get_info():
    form = get_sub_form()
    
    if form.validate():
        station = form.station_select.data
        ess = form.ess_select.data
        date = form.date_select.data
        error_type = form.type_select.data
        action_type = form.action_radio.data
        
        if action_type == "display":
            return redirect(url_for("home.display", station=station, ess=ess, date=date, error_type=error_type, page=1))
        
        tag_path = f"'%nremc/bess/{station}/{ess}/bms/state/{error_type}2%'"
        month, year = date.split("-")

        sql_query = (
            "WITH MatchingTags AS (\n"
            "   SELECT\n"
            "       id as tagid,\n"
            "       tagpath\n"
            "   FROM [dbNREMCHistorianBESSSTS].[dbo].[sqlth_te]\n"
            "   WHERE retired is NULL\n"
            f"     AND tagpath LIKE {tag_path}\n"
            ")\n"
            "SELECT\n"
            "   d.tagid,\n"
            "   t.tagpath,\n"
            "   d.t_stamp,\n"
            "   d.floatvalue,\n"
            "   d.intvalue\n"
            "FROM MatchingTags t\n"
            f"JOIN [dbNREMCHistorianBESSSTS].[dbo].[sqlt_data_2_{year}_{month}] d\n" #! DO NOT DO THIS SHIT THIS IS BAD
            "   ON t.tagid = d.tagid\n"
            "ORDER BY d.t_stamp DESC;"
        )
        df = pd.read_sql(sql_query, db.engine) # type: ignore
        df["station"] = station
        df["type"] = error_type
        df["timestamp"] = pd.to_datetime(df["t_stamp"], unit="ms")
        
        if error_type == "fault":
            for bit, label in FAULT_BIT_MAP.items():
                df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1))
        else:
            for bit, label in ALARM_BIT_MAP.items():
                df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1))
        
        df = df.drop(columns=["t_stamp", "floatvalue", "tagid","tagpath", "intvalue"])
        
        csv_file = io.BytesIO()
        df.to_csv(csv_file, index=False, header=True)
        csv_file.seek(0)
        
        return send_file(
            csv_file, mimetype="text/csv", as_attachment=True, download_name=f"{station}-{year}{month}-{ess}-{error_type}.csv"
        )
    else:
        return "FUCK YOU", 400
