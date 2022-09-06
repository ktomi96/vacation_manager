from flask import Flask

#Init Flask
def creat_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'I WILL NOT TELL'

    from .view import views

    app.register_blueprint(views, url_prefix='/')
    return app