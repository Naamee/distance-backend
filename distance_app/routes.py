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


@bp.route('/fridge', methods=('GET', 'POST', 'PUT'))
@login_required
def fridge():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 8, type=int)
        item = request.args.get('item', None, type=str)
        category = request.args.get('category', None, type=str)
        status = request.args.get('status', None, type=str)

        quantity_sum = sa.func.sum(
            sa.case((FridgeEntry.type == 'add', FridgeEntry.quantity), else_=0) # sum of 'add' quantities from fridge entries
            - sa.case((FridgeEntry.type == 'used', FridgeEntry.quantity), else_=0) # minus sum of 'used' quantities from fridge entries
        ).label('quantity')

        grouped_query = sa.select(
            FridgeItem.id,
            FridgeItem.name,
            FridgeItem.category,
            quantity_sum.label('quantity')
        ).outerjoin(FridgeItem.entries).group_by(FridgeItem.name, FridgeItem.category) #outer join to include items with zero entries

        # filtering
        if item:
            grouped_query = grouped_query.where(FridgeItem.name.ilike(f'%{item}%'))
        if category:
            grouped_query = grouped_query.where(FridgeItem.category == category)
        if status == 'Available':
            grouped_query = grouped_query.having(quantity_sum > 0)
        elif status == 'Unavailable':
            grouped_query = grouped_query.having(quantity_sum <= 0)

        # Total unique items for pagination after filtering
        total_items = db.session.scalar(sa.select(sa.func.count()).select_from(grouped_query.subquery()))

        # Apply pagination
        if per_page:
            paginated_items = db.session.execute(
                grouped_query.offset((page - 1) * per_page).limit(per_page)
            ).all()
        else:
            paginated_items = db.session.execute(grouped_query).all()

        # Build response
        items_list = [
            {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'quantity': row[3],
            }
            for row in paginated_items
        ]

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
        required_fields = {'name', 'category'}

        # Basic validation
        if not data or not required_fields.issubset(data):
            return jsonify({'message': 'Missing required fields.'}), 400
        if not data['name'].strip() or not data['category'].strip():
            return jsonify({'message': 'Invalid values provided.'}), 400

        new_item = FridgeItem(
            name=data['name'],
            category=data['category'],
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Fridge item added successfully.'}), 201

@bp.route('/fridge/<int:item_id>', methods=('PUT',))
@login_required
def edit_fridge_item(item_id):
    data = request.get_json()
    required_fields = {'name', 'category'}

    # validations
    if not data or not required_fields.issubset(data):
        return jsonify({'message': 'Missing required fields.'}), 400
    if not data['name'].strip() or not data['category'].strip():
        return jsonify({'message': 'Invalid values provided.'}), 400

    similiar_item = db.session.scalar(
        sa.select(FridgeItem).where(
            FridgeItem.name == data['name'],
            FridgeItem.category == data['category'],
            FridgeItem.id != item_id
        )
    )
    if similiar_item:
        return jsonify({'message': 'An item with the same name and category already exists.'}), 400

    # fetch the item to be updated
    item = db.session.get(FridgeItem, item_id)
    if not item:
        return jsonify({'message': 'Item not found.'}), 404

    # update item details
    item.name = data['name']
    item.category = data['category']
    db.session.commit()
    return jsonify({'message': 'Fridge item updated successfully.'}), 200


@bp.route('/fridge/<int:item_id>/entries', methods=('GET',))
@login_required
def fridge_item_entries(item_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    item = db.session.get(FridgeItem, item_id)
    if not item:
        return jsonify({'message': 'Item not found.'}), 404

    entries_query = sa.select(FridgeEntry).where(FridgeEntry.item_id == item_id).order_by(FridgeEntry.created_at.desc())
    total_entries = db.session.scalar(sa.select(sa.func.count()).select_from(entries_query.subquery()))

    if per_page:
        paginated_entries = db.session.execute(
            entries_query.offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()
    else:
        paginated_entries = db.session.execute(entries_query).scalars().all()

    entries_list = [
        {
            'id': entry.id,
            'type': entry.type,
            'quantity': entry.quantity,
            'date': entry.updated_at.isoformat(),
        }
        for entry in paginated_entries
    ]

    total_pages = (total_entries + per_page - 1) // per_page if per_page else 1

    return jsonify({
        'name': item.name,
        'category': item.category,
        'data': entries_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total_entries,
            'total_pages': total_pages,
        }
    }), 200


@bp.route('/fridge_item', methods=('POST',))
@login_required
def update_fridge_quantity():
    data = request.get_json()
    required_fields = {'id', 'quantity', 'type'}

    # validations
    if not data or not required_fields.issubset(data):
        return jsonify({'message': 'Missing required fields.'}), 400
    if not data['id'] or data['quantity'] == 0:
        return jsonify({'message': 'Invalid values provided.'}), 400
    if data['type'] not in {'add', 'used'}:
        return jsonify({'message': 'Type must be either "add" or "used".'}), 400

    item = db.session.get(FridgeItem, data['id'])
    if not item:
        return jsonify({'message': 'Item not found.'}), 404
    if data['type'] == 'used':
        # Check current quantity
        quantity_sum = db.session.scalar(
            sa.select(
                sa.func.sum(
                    sa.case((FridgeEntry.type == 'add', FridgeEntry.quantity), else_=0)
                    - sa.case((FridgeEntry.type == 'used', FridgeEntry.quantity), else_=0)
                )
            ).where(FridgeEntry.item_id == data['id'])
        ) or 0
        if data['quantity'] > quantity_sum:
            return jsonify({'message': 'Insufficient quantity available to use.'}), 400

    # if all validations pass, create a new FridgeEntry
    new_item = FridgeEntry(
        item_id=data['id'],
        quantity=data['quantity'],
        type=data['type'],
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Fridge item quantity updated successfully.'}), 201
