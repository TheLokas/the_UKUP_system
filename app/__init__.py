from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object('config')

from app import UKUP
app.register_blueprint(UKUP.UKUP.UKUP, url_prefix='/UKUP')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import models
with app.app_context():
    db.create_all()



#with app.app_context():
#    db.create_all()

#from app import views
