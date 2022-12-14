#!/usr/bin/env python

from website import app
from website.make_blank_db import db_create

from livereload import Server, shell
from website.config_init import is_database


if __name__ == "__main__":

    if not is_database():
        db_create()

    server = Server(app.wsgi_app)
    server.watch('.env')
    server.serve(host='localhost')
