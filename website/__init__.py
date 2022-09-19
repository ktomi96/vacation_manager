


import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from website.config_init import init_dotenv

init_dotenv()

# flask init
app = Flask(__name__)
app.secret_key = os.urandom(28)

# flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

# flask email
def init_email():
    app.config.update(
        DEBUG=False,
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
    )

init_email()
    


# for sqlalchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/data.db'

db = SQLAlchemy(app)

###end init###
##############
#start init###
from website import directions