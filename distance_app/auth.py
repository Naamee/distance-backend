from flask import Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from distance_app import db
from .models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
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

