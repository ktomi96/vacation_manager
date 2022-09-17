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

class Setup(FlaskForm):
    GOOGLE_CLIENT_ID = StringField("Give the GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = StringField("Give the GOOGLE_CLIENT_SECRET")
    GOOGLE_INSECURE_AUTH = IntegerField("Allow insecure connection (http)")
    MAIL_USERNAME = StringField("Give the sender email address")
    MAIL_PASSWORD = StringField(
        "Give the password for the sender email account")

    submit = SubmitField("Submit")



