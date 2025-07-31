from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField


class SubmissionForm(FlaskForm):
    station_select = SelectField(
        "Station",
        choices=[
            ("aboite", "Aboite"),
            ("gateway", "Gateway"),
            ("indiancreek", "Indian Creek"),
            ("perry", "Perry"),
            ("woodland", "Woodland"),
        ],
    )
    ess_select = SelectField(
        "PCS/ESS",
        choices=[
            ("pcs_a/ess1", "PCS A & ESS 1"),
            ("pcs_a/ess2", "PCS A & ESS 2"),
            ("pcs_b/ess3", "PCS B & ESS 3"),
            ("pcs_b/ess4", "PCS B & ESS 4"),
            ("pcs_c/ess5", "PCS C & ESS 5"),
            ("pcs_c/ess6", "PCS C & ESS 6"),
        ],
    )
    date_select = SelectField("Date")
    type_select = SelectField("Type", choices=[("alarm", "Alarm"), ("fault", "Fault")])
    action_radio = RadioField("Action", choices=[("download", "Download"), ("display", "Display")], default="download")
    submit_button = SubmitField("Submit")
