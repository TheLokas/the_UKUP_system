from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from app import UKUP

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(UKUP.UKUP.UKUP, url_prefix='/UKUP')
#db.init_app(app)

#from . import models

#with app.app_context():
#    db.create_all()

#from app import views
