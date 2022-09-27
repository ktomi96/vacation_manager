# Python standard libraries
import json
import os
from datetime import datetime, date, timedelta
from threading import Thread


# Third party libraries
from flask import Flask, redirect, request, url_for, render_template, escape, flash, session
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
#from oauthlib.oauth2 import WebApplicationClient
from authlib.integrations.flask_client import OAuth
import requests
from flask_mail import Message
from flask_mail import Mail

# Internal imports
from website import app, login_manager, db, init_email, oauth
from website.models import User, Vacation_request
from website.forms import Edit, New_request, Edit_request, Google_setup, Microsoft_setup, Init_setup
from website.config_init import is_database, is_config, set_dotenv_google, set_dotenv_microsoft, dotenv_path, init_dotenv

# Loads dotenv
init_dotenv()


# Flask app setup


# User session management setup
# https://flask-login.readthedocs.io/en/latest


@login_manager.unauthorized_handler
def unauthorized():
    user_session = get_viewer()
    return render_template("permission.html", user_session=user_session)


def get_viewer():
    if current_user.is_anonymous:
        viewer = -1
        current = "Guest"
    else:
        current = current_user.get_self()
        viewer = current.auth_level

    return {"user": current, "viewer": viewer}

# helper function to send emails asynchronously


def thread_email(mail, msg):
    with app.app_context():
        mail.send(msg)


def send_email(status, email_address, name, request_from, request_to):
    mail = Mail(app)
    msg = Message("Status update", recipients=email_address)
    msg.html = render_template("email.html", status=status,
                               name=name, request_from=request_from, request_to=request_to)

    Thread(target=thread_email, args=(mail, msg)).start()


def is_weekend(day):
    return date.weekday(day) > 4

# fullcalendar not rendering end day of the request, only showing the previus day, there wasnt any settinh in fullcallendar that would help.


def calendar_helper(vacation):
    if vacation.request_from == vacation.request_to:
        return vacation.request_to
    else:
        date_format = "%Y-%m-%d %H:%M:%S"

        date_format = datetime.combine(
            vacation.request_to, datetime.min.time())
        date_add = (date_format + timedelta(days=1))

        return datetime.strptime(str(date_add), '%Y-%m-%d %H:%M:%S')


@app.route("/setup", methods=['GET', 'POST'])
def setup():
    if is_config():
        return redirect(url_for("home"))

    init_form = Init_setup()

    if request.method == 'POST' and request.form["loggin_type"] == "GOOGLE":
        return redirect(url_for("setup_google"))

    if request.method == 'POST' and request.form["loggin_type"] == "MICROSOFT":
        return redirect(url_for("setup_microsoft"))

    return render_template("setup.html", form=init_form)


@app.route("/setup_google", methods=['GET', 'POST'])
def setup_google():
    if is_config():
        return redirect(url_for("home"))

    google_form = Google_setup()

    if request.method == 'POST':
        set_dotenv_google(request)
        init_dotenv()
        init_email()
        return redirect(url_for("home"))

    return render_template("setup_google.html", form=google_form)


@app.route("/setup_microsoft", methods=['GET', 'POST'])
def setup_microsoft():
    if is_config():
        return redirect(url_for("home"))

    microsoft_form = Microsoft_setup()

    if request.method == 'POST':
        set_dotenv_microsoft(request)
        init_dotenv()
        init_email()
        return redirect(url_for("home"))

    return render_template("setup_microsoft.html", form=microsoft_form)


@app.route("/")
def home():
    if not is_config():
        return redirect(url_for("setup"))

    user_session = get_viewer()
    # loops over the requests and puts them in a dict. for the calendar render
    events_approved = [{'title': vacation.parent.name, 'start': str(vacation.request_from), 'end': str(calendar_helper(vacation))}
                       for vacation in Vacation_request.query.filter_by(status='APPROVED').order_by(Vacation_request.request_from.asc()).all()]
    events_pending = [{'title': vacation.parent.name, 'start': str(vacation.request_from), 'end': str(calendar_helper(vacation))}
                      for vacation in Vacation_request.query.filter_by(status='PENDING').order_by(Vacation_request.request_from.asc()).all()]
    return render_template("home.html", user_session=user_session, events_approved=events_approved, events_pending=events_pending)


@app.route("/login")
def login():
    user_session = get_viewer()
    loggin_type = os.getenv("login_type")
    return render_template("login.html", user_session=user_session, loggin_type=loggin_type)


@app.route("/microsoft_login")
def microsoft_login():

    tenant_name = os.getenv("tenant_name")

    url_auth = f'https://login.microsoftonline.com/{tenant_name}/v2.0/.well-known/openid-configuration'
    oauth.register(
        name='microsoft',
        provider='microsoft',
        client_id=os.getenv("client_id"),
        client_secret=os.getenv("client_secret"),
        server_metadata_url=url_auth,
        client_kwargs={'scope': 'openid profile email'}
    )

    redirect_uri = url_for('microsoft_callback', _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)


@app.route("/microsoft_login/callback")
def microsoft_callback():
    token = oauth.microsoft.authorize_access_token()

    userinfo = token['userinfo']

    unique_id = userinfo["sub"]
    users_email = userinfo["email"]
    # couldn't figure out how to get  profile_pic with only openid
    picture = 'none'
    users_name = userinfo["name"]

    # Create a user in our db with the information provided
    # by Azure

    # is_user to detect if its the first user being created
    # First user gets auth_level = 2 (admin)

    if not User.is_user():
        acces_level = 2
    else:
        acces_level = 0

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture, auth_level=acces_level, vacation_quota=20
    )

    # Doesn't exist? Add to database
    if not User.query.get(unique_id):
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("home"))


@app.route("/google_login")
def google_login():
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")

    oauth.register(
        name='google',
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/google_login/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token['userinfo']

    if userinfo["email_verified"]:
        unique_id = userinfo["sub"]
        users_email = userinfo["email"]
        picture = userinfo["picture"]
        users_name = userinfo["name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google

    # is_user to detect if its the first user being created
    # First user gets auth_level = 2 (admin)

    if not User.is_user():
        acces_level = 2
    else:
        acces_level = 0

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture, auth_level=acces_level, vacation_quota=20
    )

    # Doesn't exist? Add to database
    if not User.query.get(unique_id):
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("home"))


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/manage_users")
@login_required
def manage_users():
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 2:
        our_users = User.query.order_by(User.date_created)
        return render_template("manage_users.html", our_users=our_users, user_session=user_session)
    else:
        return redirect(url_for("home"))


@app.route("/<id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id: str):
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 2:
        edit_user = User.query.filter_by(id_=id).first()
        # puts the previus auth_level into form to be displayed
        form = Edit(auth_level=edit_user.auth_level)
        if request.method == 'POST':
            if edit_user:

                edit_user.name = request.form['name']
                edit_user.email = request.form['email']
                edit_user.auth_level = request.form['auth_level']
                edit_user.vacation_quota = request.form['vacation_quota']
                db.session.commit()
                return redirect(url_for("manage_users"))
        return render_template("edit.html", edit_user=edit_user, form=form, value=edit_user, user_session=user_session)

    else:
        return redirect(url_for("home"))


@app.route("/request_vacation")
@login_required
def request_vacation():
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 1 or 2:
        user = current_user.get_self()

        return render_template("request_vacation.html", user=user, user_session=user_session)


@app.route("/<id>/new_request", methods=['GET', 'POST'])
@login_required
def new_request(id: str):
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 1 or 2:
        user_request = User.query.filter_by(id_=id).first()

        form = New_request()
        if request.method == 'POST':
            date_format = "%Y-%m-%d"

            request_from = datetime.strptime(
                escape(form.date_from.data), date_format)
            request_to = datetime.strptime(
                escape(form.date_to.data), date_format)

            if form.date_from.data < date.today():
                flash("Date that you choose must be today or in the future")
            elif ((request_to - request_from).days + 1) > user_request.leave_requests()["balance"]:
                flash("You dont have enough balance for that")

            elif request_to < request_from:
                flash("You can't travel in the time (unless you have a Flux capacitor)")
            elif is_weekend(form.date_from.data) or is_weekend(form.date_to.data):
                flash("Invalid request, must start/end with weekdays")
            else:
                new_request = Vacation_request(
                    user_id=current_user.id_, request_from=request_from, request_to=request_to, status="PENDING")
                db.session.add(new_request)
                db.session.commit()
                return redirect(url_for("request_vacation"))

        return render_template("new_request.html", form=form, user_request=user_request, user_session=user_session)


@app.route("/<id>/delete", methods=['GET', 'POST'])
@login_required
def delete_request(id: str):
    if current_user.get_auth_lvl() == 1 or 2:
        user = current_user.get_self()
        to_delete = Vacation_request.query.filter_by(id_=id).first()

        can_be_deleted = False

        if user.id_ == to_delete.user_id:
            can_be_deleted = True
        if to_delete.status == 'APPROVED' and current_user.get_auth_lvl() == 1:
            can_be_deleted = False
            flash("You can't delete, it has already been approved")

        if current_user.get_auth_lvl() == 2:
            can_be_deleted = True

        if request.method == 'GET' and can_be_deleted == True:

            db.session.delete(to_delete)
            db.session.commit()

            return redirect(url_for("request_vacation"))

        else:
            return redirect(url_for("request_vacation"))


@app.route("/manage_request")
@login_required
def manage_request():
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 2:
        requests = Vacation_request.query.order_by(
            Vacation_request.date_created.desc())
        return render_template("manage_request.html", requests=requests, user_session=user_session)
    else:
        return redirect(url_for("home"))


@app.route("/<id>/edit_request", methods=['GET', 'POST'])
@login_required
def edit_request(id: str):
    user_session = get_viewer()
    if current_user.get_auth_lvl() == 2:
        request_edit = Vacation_request.query.filter_by(id_=id).first()
        # puts the previus date into form to be displayed
        form = Edit_request(request_status=request_edit.status,
                            date_from=request_edit.request_from, date_to=request_edit.request_to)
        state_was = request_edit.status
        if request.method == 'POST':
            if request_edit:
                date_format = "%Y-%m-%d"

                request_edit.request_from = datetime.strptime(
                    escape(form.date_from.data), date_format)
                request_edit.request_to = datetime.strptime(
                    escape(form.date_to.data), date_format)
                request_edit.status = request.form['request_status']

                db.session.commit()
                if state_was != request_edit.status:
                    send_email(request_edit.status, [
                               request_edit.parent.email], request_edit.parent.name, request_edit.request_from, request_edit.request_to)
                flash("Email sent")
                return redirect(url_for("manage_request"))
        return render_template("edit_request.html", request_edit=request_edit, form=form, user_session=user_session)

    else:
        return redirect(url_for("home"))
