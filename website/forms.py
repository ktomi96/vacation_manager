from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField, EmailField
from wtforms.validators import InputRequired, Email, DataRequired, NumberRange, AnyOf, Length


class Edit(FlaskForm):
    name = StringField("User name", validators=[InputRequired()])
    email = EmailField("User email", validators=[InputRequired(), Email()])
    auth_level = SelectField("User acces level", choices=[
                             (0, "Guest"), (1, "User"), (2, "Admin")], validators=[InputRequired(), AnyOf([
                                 (0, "Guest"), (1, "User"), (2, "Admin")])])
    vacation_quota = IntegerField(
        "User vacation quota", validators=[InputRequired(), NumberRange(min=20)])

    submit = SubmitField("Submit")


class New_request(FlaskForm):
    date_from = DateField("First day of the vacation",
                          format="%Y-%m-%d", validators=[InputRequired()])
    date_to = DateField("Last day of the vacation",
                        format="%Y-%m-%d", validators=[InputRequired()])

    submit = SubmitField("Submit")


class Edit_request(FlaskForm):
    date_from = DateField("First day of the vacation",
                          format="%Y-%m-%d", validators=[InputRequired()])
    date_to = DateField("Last day of the vacation",
                        format="%Y-%m-%d", validators=[InputRequired()])
    request_status = SelectField("Request status: ", choices=[(
        "APPROVED", "APPROVED"), ("PENDING", "PENDING"), ("DENIED", "DENIED")], validators=[InputRequired(), AnyOf(["APPROVED", "PENDING", "DENIED"])])

    submit = SubmitField("Submit")


class Setup(FlaskForm):
    GOOGLE_CLIENT_ID = StringField(
        "Give the GOOGLE_CLIENT_ID", validators=[InputRequired(), Length(min=73)])
    GOOGLE_CLIENT_SECRET = StringField(
        "Give the GOOGLE_CLIENT_SECRET", validators=[InputRequired(), Length(min=35)])
    GOOGLE_INSECURE_AUTH = IntegerField(
        "Allow insecure connection (http)", validators=[InputRequired(), NumberRange(min=0, max=1)])
    MAIL_USERNAME = StringField(
        "Give the sender email address", validators=[InputRequired(), Email()])
    MAIL_PASSWORD = StringField(
        "Give the password for the sender email account", validators=[InputRequired()])

    submit = SubmitField("Submit")
