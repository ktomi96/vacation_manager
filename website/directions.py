# Python standard libraries
import json
import os
from datetime import datetime


# Third party libraries
from flask import Flask, redirect, request, url_for, render_template, escape
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from dotenv import load_dotenv

# Internal imports
# sqlite implementaion
#from db import init_db_command
#from user import User
# sqlachemy impl
from website import app, login_manager, db
from website.models import User, Vacation_request
from website.forms import Edit, New_request, Edit_request

# Configuration
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup


# User session management setup
# https://flask-login.readthedocs.io/en/latest


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


# Naive database setup
# try:
    # init_db_command()
# except sqlite3.OperationalError:
    # Assume it's already been created
    # pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
# @login_manager.user_loader
# def load_user(user_id):
# return User.get(user_id)
def get_viewer():
    if current_user.is_anonymous:
        viewer = -1
    else:
        viewer = current_user.get_auth_lvl()

    return viewer


@app.route("/")
def home():
    viewer = get_viewer()
    return render_template("base.html", viewer=viewer)


@app.route("/login")
def login():

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
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


@app.route("/admin")
@login_required
def admin():
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 2:
        return render_template("admin.html", viewer=viewer)
    else:
        return redirect(url_for("home"))


@app.route("/manage_users")
@login_required
def manage_users():
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 2:
        our_users = User.query.order_by(User.date_created)
        return render_template("manage_users.html", our_users=our_users, viewer=viewer)
    else:
        return redirect(url_for("home"))


@app.route("/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id: int):
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 2:
        edit_user = User.query.filter_by(id_=str(id)).first()
        form = Edit()
        form = Edit(auth_level=edit_user.auth_level)
        if request.method == 'POST':
            if edit_user:

                edit_user.name = request.form['name']
                edit_user.email = request.form['email']
                edit_user.auth_level = request.form['auth_level']
                edit_user.vacation_quota = request.form['vacation_quota']
                db.session.commit()
                return redirect(url_for("manage_users"))
        return render_template("edit.html", edit_user=edit_user, form=form, value=edit_user, viewer=viewer)

    else:
        return redirect(url_for("home"))


@app.route("/request_vacation")
@login_required
def request_vacation():
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 1 or 2:
        user = current_user.get_self()

        return render_template("request_vacation.html", user=user, viewer=viewer)


@app.route("/<int:id>/new_request", methods=['GET', 'POST'])
@login_required
def new_request(id: int):
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 1 or 2:
        user_request = User.query.filter_by(id_=str(id)).first()

        form = New_request()
        if request.method == 'POST':
            date_format = "%Y-%m-%d"

            request_from = datetime.strptime(
                escape(form.date_from.data), date_format)
            request_to = datetime.strptime(
                escape(form.date_to.data), date_format)
            print(request_from)

            new_request = Vacation_request(
                user_id=current_user.id_, request_from=request_from, request_to=request_to, status="PENDING")
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for("request_vacation"))

        return render_template("new_request.html", form=form, user_request=user_request, viewer=viewer)


@app.route("/<int:id>/delete", methods=['GET', 'POST'])
@login_required
def delete_request(id: int):
    if current_user.get_auth_lvl() == 1 or 2:
        user = current_user.get_self()
        to_delete = Vacation_request.query.filter_by(id_=id).first()

        can_be_deleted = False

        if user.id_ == to_delete.user_id:
            can_be_deleted = True
        elif to_delete.status == 'ACCEPTED':
            can_be_deleted = False

        if current_user.get_auth_lvl() == 2:
            can_be_deleted = True

        if request.method == 'GET' and can_be_deleted == True:

            print(to_delete)
            db.session.delete(to_delete)
            db.session.commit()

            return redirect(url_for("request_vacation"))

        else:
            return redirect(url_for("request_vacation"))


@app.route("/manage_request")
@login_required
def manage_request():
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 2:
        requests = Vacation_request.query.order_by(
            Vacation_request.date_created.desc())
        return render_template("manage_request.html", requests=requests, viewer=viewer)
    else:
        return redirect(url_for("home"))


@app.route("/<int:id>/edit_request", methods=['GET', 'POST'])
@login_required
def edit_request(id:int):
    viewer = get_viewer()
    if current_user.get_auth_lvl() == 2:
        request_edit = Vacation_request.query.filter_by(id_=str(id)).first()
        form = Edit_request()
        form = Edit_request(date_from=request_edit.request_from)
        form = Edit_request(date_to=request_edit.request_to)
        form = Edit_request(request_status=request_edit.status)
        if request.method == 'POST':
            if request_edit:

                request_edit.date_from = request.form['date_from']
                request_edit.date_to = request.form['date_to']
                request_edit.status = request.form['request_status']

                db.session.commit()
                return redirect(url_for("manage_request"))
        return render_template("edit_request.html", request_edit=request_edit, form=form, value=request_edit, viewer=viewer)

    else:
        return redirect(url_for("home"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
