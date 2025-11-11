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


@bp.route('/fridge', methods=('GET', 'POST'))
@login_required
def fridge():
    if request.method == 'GET':
        #query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', type=int)

        query = sa.select(FridgeItem).where(FridgeItem.type == 'add')
        total_items = db.session.scalar(sa.select(sa.func.count()).select_from(query.subquery()))

        # Apply pagination if per_page is specified, else get all items
        if not per_page:
            paginated_items = db.session.scalars(query).all()
        else:
            paginated_items = db.session.scalars(query.offset((page - 1) * per_page).limit(per_page)).all()

        unique_pairs = {(item.name, item.category) for item in paginated_items} # this is to get the total quantity per unique name-category pair
        items_list = []
        for name, category in unique_pairs:
            total_quantity = sum(
                item.quantity for item in paginated_items if item.name == name and item.category == category
            )
            items_list.append({
                'name': name,
                'type': 'add',
                'category': category,
                'quantity': total_quantity,
            })

        # Calculate pagination metadata
        total_pages = (total_items + per_page - 1) // per_page if per_page else 1

        return jsonify({
            'data': items_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
            }
        }), 200

    elif request.method == 'POST':
        data = request.get_json()
        required_fields = {'name', 'category', 'quantity'}
        if not data or not required_fields.issubset(data):
            return jsonify({'message': 'All fields are required.'}), 400

        new_item = FridgeItem(
            name=data['name'],
            type='add',
            category=data['category'],
            quantity=data['quantity']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Fridge item added successfully.'}), 201


@bp.route('/fridge/<int:item_id>', methods=('PUT', 'DELETE'))
@login_required
def fridge_item(item_id):
    item = db.session.get(FridgeItem, item_id)
    if not item:
        return jsonify({'message': 'Item not found.'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided.'}), 400

        item.name = data.get('name', item.name)
        item.type = data.get('type', item.type)
        item.category = data.get('category', item.category)
        item.quantity = data.get('quantity', item.quantity)

        db.session.commit()
        return jsonify({'message': 'Fridge item updated successfully.'}), 200

    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Fridge item deleted successfully.'}), 200