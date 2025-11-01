from flask import ( Blueprint )

bp = Blueprint('main', __name__)

@bp.route('/items', methods=('GET', 'POST', 'PUT', 'DELETE'))
def items():
    