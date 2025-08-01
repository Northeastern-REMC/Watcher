import io
from collections.abc import Mapping, Sequence
from datetime import datetime

import pandas as pd
from flask import Blueprint, redirect, render_template, request, send_file, url_for

from watcher.constants import (
    ALARM_BIT_MAP,
    FAULT_BIT_MAP,
    IGNITION_EPOCH,
    ITEMS_PER_PAGE,
    NREMC_TIMEZONE,
)
from watcher.db import db
from watcher.forms import SubmissionForm

bp = Blueprint("home", __name__, url_prefix="/")


def get_sub_form():
    current_date = datetime.now(NREMC_TIMEZONE)
    form = SubmissionForm(request.form)
    form.date_select.choices = [
        (d.strftime(r"%m-%Y"), d.strftime(r"%B %Y"))
        for d in pd.date_range(IGNITION_EPOCH, current_date, freq="MS").tolist()
    ]
    return form


def decode_bits(value: int, bit_map: Mapping[int, str]):
    return [label for bit, label in bit_map.items() if (value >> bit) & 1]


def build_sql_query(year: str, month: str, tag_path: str) -> str:
    return f"""
    WITH MatchingTags AS (
        SELECT id AS tagid, tagpath
        FROM [dbNREMCHistorianBESSSTS].[dbo].[sqlth_te]
        WHERE retired IS NULL AND tagpath LIKE {tag_path}
    )
    SELECT
        d.tagid,
        t.tagpath,
        d.t_stamp,
        d.floatvalue,
        d.intvalue
    FROM MatchingTags t
    JOIN [dbNREMCHistorianBESSSTS].[dbo].[sqlt_data_2_{year}_{month}] d
        ON t.tagid = d.tagid
    ORDER BY d.t_stamp DESC;
    """


@bp.get("/")
def index():
    return render_template("index.jinja.html", form=get_sub_form())


@bp.get("/display")
def display():
    station = request.args.get("station")
    ess = request.args.get("ess")
    error_type = request.args.get("error_type")
    date = request.args.get("date", "")
    page = int(request.args.get("page", 1))

    month, year = None, None
    try:
        month, year = date.split("-")
    except (ValueError, AttributeError):
        return "Invalid date format", 400

    tag_path = f"'%nremc/bess/{station}/{ess}/bms/state/{error_type}2%'"
    sql_query = build_sql_query(year, month, tag_path)

    df = None
    try:
        df = pd.read_sql(sql_query, db.engine)  # type: ignore
    except Exception as e:
        return f"Database error: {e}", 500

    df["timestamp"] = pd.to_datetime(df["t_stamp"], unit="ms").dt.strftime(
        "%B %d %Y %I:%M:%S %p %Z"
    )
    output: Sequence[tuple[str, Sequence[str]]] = []
    bit_map = FAULT_BIT_MAP if error_type == "fault" else ALARM_BIT_MAP

    for _, row in df.iterrows():
        int_val = row["intvalue"]
        labels = decode_bits(int_val, bit_map)
        t: str = row["timestamp"]
        output.append((t, labels))

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated = output[start:end]

    return render_template(
        "display.jinja.html",
        paginated=paginated,
        station=station,
        ess=ess,
        error_type=error_type,
        date=date,
        page=page,
        next_page=page + 1,
        prev_page=max(page - 1, 1),
    )


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
            return redirect(
                url_for(
                    "home.display",
                    station=station,
                    ess=ess,
                    date=date,
                    error_type=error_type,
                    page=1,
                )
            )

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
            f"JOIN [dbNREMCHistorianBESSSTS].[dbo].[sqlt_data_2_{year}_{month}] d\n"  #! DO NOT DO THIS SHIT THIS IS BAD
            "   ON t.tagid = d.tagid\n"
            "ORDER BY d.t_stamp DESC;"
        )
        df = pd.read_sql(sql_query, db.engine)  # type: ignore
        df["station"] = station
        df["type"] = error_type
        df["timestamp"] = pd.to_datetime(df["t_stamp"], unit="ms")

        if error_type == "fault":
            for bit, label in FAULT_BIT_MAP.items():
                df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1)) # type: ignore
        else:
            for bit, label in ALARM_BIT_MAP.items():
                df[label] = df["intvalue"].apply(lambda x: bool((x >> bit) & 1)) # type: ignore

        df = df.drop(columns=["t_stamp", "floatvalue", "tagid", "tagpath", "intvalue"])

        csv_file = io.BytesIO()
        df.to_csv(csv_file, index=False, header=True)
        csv_file.seek(0)

        return send_file(
            csv_file,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{station}-{year}{month}-{ess}-{error_type}.csv",
        )
    else:
        return "Invalid form", 400
