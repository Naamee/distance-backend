from flask import Blueprint, request, jsonify
from distance_app.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/meet', methods=('GET', 'POST', 'PUT', 'DELETE'))
def meet():
    if request.method == 'POST':
        data = request.get_json()

        db = get_db()

        db.execute(
            "INSERT INTO meet_date (date) VALUES (?)", (data['date'],)
        )
        db.commit()

        return jsonify({'message': 'meet date added successfully.'}), 201