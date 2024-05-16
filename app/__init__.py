from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from app import UKUP
from .models import db
from flask_migrate import Migrate


# db = SQLAlchemy()
def create_app(database_uri=None):
    app = Flask(__name__)
    # app.app_context().push()
    app.config.from_object('config')
    if database_uri is not None:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.register_blueprint(UKUP.UKUP.UKUP, url_prefix='/UKUP')
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    # from . import models

    # with app.app_context():
    #     db.create_all()
    return app


#from app import views
