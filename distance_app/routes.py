from flask import Blueprint, request, jsonify
from flask_login import login_required
from distance_app import db

bp = Blueprint('main', __name__)


@bp.route('/meet', methods=('GET', 'POST', 'PUT', 'DELETE'))
@login_required
def meet():
    if request.method == 'POST':
        # data = request.get_json()

        # db = db.get_db()

        # db.execute(
        #     "INSERT INTO meet_date (date) VALUES (?)", (data['date'],)
        # )
        # db.commit()

        return jsonify({'message': 'meet date added successfully.'}), 201