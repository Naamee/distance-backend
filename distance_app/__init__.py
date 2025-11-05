import os
from .config import Config
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "you-will-never-guess"
)  # For session management
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])  # Enable CORS

app.config.from_object(Config)  # Load configuration from config.py
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=1)

db = SQLAlchemy(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db)  # Initialize Flask-Migrate
login = LoginManager(app)  # Initialize Flask-Login
login.login_view = "auth.login"  # Specify the login view for @login_required

# return JSON response for unauthorized access attempts
# allow frontend to handle redirects appropriately
@login.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401


# import models and blueprints
from distance_app import models
from distance_app import auth, routes

app.register_blueprint(auth.bp)
app.register_blueprint(routes.bp)
