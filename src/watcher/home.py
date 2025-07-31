from flask import Blueprint, render_template
from sqlalchemy import text

from watcher.db import db

bp = Blueprint("home", __name__, url_prefix="/")


@bp.get("/")
def index():
    with db.engine.connect() as conn:
        result = conn.execute(
            text(
                (
                    "WITH MatchingTags AS ( "
                    "SELECT "
                    "id AS tagid, "
                    "tagpath "
                    "FROM [dbNREMCHistorianBESSSTS].[dbo].[sqlth_te] "
                    "WHERE retired IS NULL "
                    "AND tagpath LIKE '%nremc/bess/gateway/pcs_a/ess1/bms/state/alarm2%')\n"
                    "SELECT "
                    "d.tagid, "
                    "t.tagpath, "
                    "d.t_stamp, "
                    "d.floatvalue, "
                    "d.intvalue "
                    "FROM MatchingTags t "
                    "JOIN [dbNREMCHistorianBESSSTS].[dbo].[sqlt_data_2_2025_07] d "
                    "ON t.tagid = d.tagid "
                    "ORDER BY d.t_stamp DESC; "
                )
            )
        )

        result = str(result.fetchall())
        print(result)
    return render_template("index.jinja.html", hawk=result)
