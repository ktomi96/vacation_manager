import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

#flask init
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

#flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

#for sqlalchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)

###end init###
##############
#start init###

from website import directions
