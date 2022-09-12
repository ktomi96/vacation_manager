from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin
from datetime import datetime

#app = Flask(__name__)

# Internal imports
from website import app, db, login_manager


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

    def get_id(self):
        return (self.id_)

    def get_self(self):
        user = User.query.filter_by(id_=self.id_).first()
        return user

    def is_user():
        return db.session.query(User.id_).first() is not None

    def get_auth_lvl(self):
        user = User.query.filter_by(id_=self.id_).first()
        return user.auth_level


class Vacation_request(db.Model):
    id_ = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(255), db.ForeignKey("user.id_"))
    request_from = db.Column(db.Date())
    request_to = db.Column(db.Date())
    status = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
