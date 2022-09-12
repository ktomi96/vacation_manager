import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id_ = db.Column(db.String(255), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    profile_pic = db.Column(db.String(255), nullable=False)
    auth_level = db.Column(db.Integer(), nullable=False)
    vacation_quota = db.Column(db.Integer(), nullable=False)
    vacation_requests = db.relationship(
        "Vacation_request", backref="user")


class Vacation_request(db.Model):
    id_ = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(255), db.ForeignKey("user.id_"))
    request_from = db.Column(db.Date())
    request_to = db.Column(db.Date())
    status = db.Column(db.String(255))


db.create_all()
