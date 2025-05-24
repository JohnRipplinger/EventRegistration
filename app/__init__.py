from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key'

Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes