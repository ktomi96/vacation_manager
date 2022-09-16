from website import app
import os.path
import dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired
from flask import Flask, redirect, request, url_for, render_template
from website.make_blank_db import db_create

dotenv_path = "vacation_manager\website\.env"
db_path = "vacation_manager\website\data.db"

app_setup = Flask(__name__, template_folder='setup_template')
app_setup.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app_setup.route("/", methods=['GET', 'POST'])
def setup():
    
    form = Setup()
    if request.method == 'POST':
        set_dotenv(dotenv_path, request)
        print("Done")
        shutdown_server()

    return render_template("setup.html",form=form)

class Setup(FlaskForm):
    GOOGLE_CLIENT_ID = StringField("Give the GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = StringField("Give the GOOGLE_CLIENT_SECRET")
    MAIL_USERNAME = StringField("Give the sender email address")
    MAIL_PASSWORD = StringField("Give the password for the sender email account")

    submit = SubmitField("Submit")


def is_database(db_path):
    return os.path.exists(db_path)

def is_config(dotenv_path):
    return os.path.exists(dotenv_path)

def set_dotenv(dotenv_path, request):
    dotenv.set_key(dotenv_path, "GOOGLE_CLIENT_ID", request.form['GOOGLE_CLIENT_ID'])
    dotenv.set_key(dotenv_path, "GOOGLE_CLIENT_SECRET", request.form['GOOGLE_CLIENT_SECRET'])
    dotenv.set_key(dotenv_path, "MAIL_USERNAME", request.form['MAIL_USERNAME'])
    dotenv.set_key(dotenv_path, "MAIL_PASSWORD", request.form['MAIL_PASSWORD'])

if __name__ == "__main__":
    if is_config(dotenv_path):
        if not is_database(db_path):
            db_create()
        else:
            pass

        app.run(ssl_context='adhoc')
    
    else:
        if not is_database(db_path):
            db_create()
        else:
            pass
        app_setup.run(ssl_context='adhoc')
        
       