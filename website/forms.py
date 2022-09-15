from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired


class Edit(FlaskForm):
    name = StringField("User name")
    email = StringField("User email")
    auth_level = SelectField("User acces level", choices=[
                             (0, "Guest"), (1, "User"), (2, "Admin")])
    vacation_quota = IntegerField("User vacation quota")

    submit = SubmitField("Submit")


class New_request(FlaskForm):
    date_from = DateField("First day of the vacation", format="%Y-%m-%d")
    date_to = DateField("Last day of the vacation", format="%Y-%m-%d")

    submit = SubmitField("Submit")


class Edit_request(FlaskForm):
    date_from = DateField("First day of the vacation", format="%Y-%m-%d")
    date_to = DateField("Last day of the vacation", format="%Y-%m-%d")
    request_status = SelectField("Request status: ", choices=[(
        "APPROVED", "APPROVED"), ("PENDING", "PENDING"), ("DENIED", "DENIED")])

    submit = SubmitField("Submit")
