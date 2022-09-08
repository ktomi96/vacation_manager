from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin

#app = Flask(__name__)

# Internal imports
from website import app, db, login_manager


class User(db.Model, UserMixin):
    id_ = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    profile_pic = db.Column(db.String(255), nullable=False)
    auth_level = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return (self.id_)
    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


    
