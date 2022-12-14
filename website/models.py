from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin
from datetime import datetime, date, timedelta


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

    def leave_requests(self):
        vacation_approved = sum([vacation.get_holidays()
                                 for vacation in self.vacation_requests if vacation.status == "APPROVED" or vacation.status == "PENDING"])

        vacation_balance = {"vacation_approved": vacation_approved, "balance": (
            self.vacation_quota - vacation_approved)}

        return vacation_balance


class Vacation_request(db.Model):
    id_ = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(255), db.ForeignKey("user.id_"))
    parent = db.relationship(
        "User", back_populates="vacation_requests", viewonly=True)
    request_from = db.Column(db.Date())
    request_to = db.Column(db.Date())
    status = db.Column(db.String(255))

    def get_holidays(self):

        day_to_loop = datetime.combine(self.request_from, datetime.min.time())
        day = 0
        while day_to_loop <= datetime.combine(self.request_to, datetime.min.time()):
            if date.weekday(day_to_loop) <= 4:
                day += 1
            day_to_loop = (day_to_loop + timedelta(days=1))
        return day

    def is_today():
        return date.today()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
