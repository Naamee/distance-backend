from flask import Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from distance_app import db, login
from .models import User

bp = Blueprint('auth', __name__)

# Load user for Flask-Login session management
@login.user_loader
def load_user(id: int):
    return db.session.get(User, int(id))

@bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already logged in.'}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
        return jsonify({'message': 'User registered successfully.'}), 201
    except sa.exc.IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Username already exists.'}), 400


@bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already logged in.'}), 200

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)

        user = db.session.scalar(sa.select(User).where(User.username == username))

        if user is None or not user.check_password(password):
            return jsonify({'message': 'Invalid username or password.'}), 401

        login_user(user, remember=remember)
        return jsonify({'message': 'Logged in successfully.'}), 200


@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200

