#!/usr/bin/env python

from website import app
import os.path
import dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired
from flask import Flask, redirect, request, url_for, render_template
from website.make_blank_db import db_create

from livereload import Server, shell


dotenv_path = ".env"
db_path = "website/data.db"

def is_database(db_path):
    return os.path.exists(db_path)

def is_config(dotenv_path):
    return os.path.exists(dotenv_path)

if __name__ == "__main__":

    if not is_database(db_path):
        db_create()
    
    server = Server(app.wsgi_app)
    server.watch('.env')
    server.serve()
