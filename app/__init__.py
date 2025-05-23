from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key'  # Use a secure random key in production
db = SQLAlchemy(app)

from app import routes  # Import routes after initializing app

migrate = Migrate(app, db)

from app import models  # Import models after db is defined