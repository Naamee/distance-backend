from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config) # Load configuration from config.py
db = SQLAlchemy(app) # Initialize SQLAlchemy
migrate = Migrate(app, db) # Initialize Flask-Migrate


# Import and register blueprints
from distance_app import auth, routes

app.register_blueprint(auth.bp)
app.register_blueprint(routes.bp)

