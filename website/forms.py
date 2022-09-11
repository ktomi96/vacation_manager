from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class Edit(FlaskForm):
    name = StringField("User name")
    email = StringField("User email")
    auth_level = SelectField("User acces level", choices=[
                             (0, "Guest"), (1, "User"), (2, "Admin")])
    vacation_quota = IntegerField("User vacation quota")

    submit = SubmitField("Submit")
