from flask import Blueprint, request, jsonify
from flask_login import login_required
from distance_app import db
import sqlalchemy as sa
from .models import *
import datetime

bp = Blueprint('main', __name__)


@bp.route('/meet', methods=('GET', 'PUT', 'DELETE'))
@login_required
def meet():
    if request.method == 'GET':
        date = db.session.scalar(sa.select(MeetDate))
        remaining_days = (
            (datetime.datetime.strptime(date.date, '%Y-%m-%d').date() - datetime.date.today()).days
            if date else 0
        )
        return jsonify({'meet_date': date.date if date else None, 'remaining_days': remaining_days}), 200

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or 'date' not in data:
            return jsonify({'message': 'Date is required.'}), 400

        new_date = data['date']

        # always maintain a single MeetDate entry
        date_entry = db.session.scalar(sa.select(MeetDate))
        if date_entry:
            date_entry.date = new_date
        else:
            date_entry = MeetDate(date=new_date)
            db.session.add(date_entry)
        db.session.commit()
        return jsonify({'message': 'Meet date updated successfully.'}), 200

    elif request.method == 'DELETE':
        date_entry = db.session.scalar(sa.select(MeetDate))
        if date_entry:
            db.session.delete(date_entry)
            db.session.commit()
            return jsonify({'message': 'Meet date deleted successfully.'}), 200
        else:
            return jsonify({'message': 'No meet date to delete.'}), 404