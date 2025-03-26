from flask import Blueprint, jsonify, request
from app import db
from app.models import Widget, Installation
from sqlalchemy.orm import joinedload
from datetime import timedelta
import decimal

bp = Blueprint('api', __name__)

@bp.route('/installations/widget/<id_widget>', methods=['GET'])
def get_installations_by_widget(id_widget):
    installations = Installation.query.with_entities(Installation.client_domain, Installation.status).filter_by(id_widget=id_widget).all()
    if not installations:
        return jsonify({'error': 'No installations found for this widget.'}), 404
    results = [{
                "client_domain": installation.client_domain,
                "widget_name": installation.widget.name_widget,
                "paid": installation.widget.paid,
                "date_install": installation.date_install.isoformat(),
                "date_expire": installation.date_expire.isoformat(),
                "trial": installation.trial,
                "status": installation.status
            } for installation in installations]
    return jsonify(results), 200

@bp.route('/installations/client_domain/<path:client_domain>', methods=['GET'])
def get_installations_by_client_domain(client_domain):
    installations = Installation.query.filter_by(client_domain=client_domain).options(joinedload(Installation.widget)).all()

    if not installations:
        return jsonify({'message': 'No installations found for this client.'}), 404

    results = []
    for installation in installations:
        if installation.widget:
            results.append({
                "client_domain": installation.client_domain,
                "widget_name": installation.widget.name_widget,
                "paid": installation.widget.paid,
                "date_install": installation.date_install.isoformat(),
                "date_expire": installation.date_expire.isoformat(),
                "trial": installation.trial,
                "status": installation.status
            })
    return jsonify(results), 200

@bp.route('/installations/extend', methods=['PATCH'])
def extend_installation():
    data = request.get_json()
    client_domain = data.get('client_domain')
    id_widget = data.get('id_widget')
    days = data.get('days', 10)

    if not client_domain or not id_widget:
        return jsonify({'error': 'You must specify the client_domain and id_widget.'}), 400

    installation = Installation.query.filter_by(client_domain=client_domain, id_widget=id_widget).first()

    if not installation:
        return jsonify({'error': 'The installation was not found.'}), 404

    installation.date_expire += timedelta(days=days)

    db.session.commit()

    return jsonify({
        'message': f'The end date has been extended by {days} day(s)',
        'new_expiration_date': installation.date_expire.isoformat()
    }), 200

@bp.route('/widgets', methods=['GET'])
def get_all_widgets():
    widgets = Widget.query.all()

    if not widgets:
        return jsonify({'message': 'Widgets not found.'}), 404

    results = []
    for widget in widgets:
        results.append({
            'id_widget': widget.id_widget,
            'name_widget': widget.name_widget,
            'paid': widget.paid,
            'price': widget.price
        })

    return jsonify(results), 200

@bp.route('/widgets', methods=['POST'])
def create_widget():
    data = request.get_json()
    id_widget = data.get('id_widget')
    name_widget = data.get('name_widget')
    paid = data.get('paid', False)
    price_str = data.get('price', '0.00')

    if not id_widget or not name_widget:
        return jsonify({'error': 'id_widget and name_widget must be specified.'}), 400

    if not isinstance(paid, bool):
        if isinstance(paid, str):
            paid = paid.lower() == 'true'
        elif isinstance(paid, int):
            paid = bool(paid)
        else:
            return jsonify({'error': 'Incorrect paid format. It must be a boolean (true or false).'}), 400

    try:
        price = decimal.Decimal(price_str)
    except decimal.InvalidOperation:
        return jsonify({'error': 'Incorrect price format. It must be a decimal number (f.e. 0.00).'}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    existing_widget = Widget.query.get(id_widget)
    if existing_widget:
        return jsonify({'error': 'A widget with this ID already exists.'}), 409

    new_widget = Widget(id_widget=id_widget, name_widget=name_widget, paid=paid, price=price)

    db.session.add(new_widget)
    db.session.commit()

    return jsonify({'message': 'The widget was created successfully.', 'id_widget': id_widget}), 201

@bp.route('/widgets/<id_widget>', methods=['PATCH'])
def update_widget(id_widget):
    widget = Widget.query.get(id_widget)

    if not widget:
        return jsonify({'error': 'Widget not found'}), 404

    data = request.get_json()

    if 'name_widget' in data:
        widget.name_widget = data['name_widget']
    if 'paid' in data:
        widget.paid = data['paid']
    if 'price' in data:
         price_str = data['price']
         try:
             price = decimal.Decimal(price_str)
             widget.price = price
         except decimal.InvalidOperation:
            return jsonify({'error': 'Incorrect price format. It must be a decimal number (f.e. 0.00).'}), 400

    db.session.commit()

    return jsonify({'id_widget': widget.id_widget,
                    'name_widget': widget.name_widget,
                    'paid': widget.paid,
                    'price': widget.price
                    }), 200

@bp.route('/widgets/<id_widget>', methods=['DELETE'])
def delete_widget(id_widget):
        widget = Widget.query.get(id_widget)

        if not widget:
            return jsonify({'error': 'Widget not found'}), 404

        db.session.delete(widget)
        db.session.commit()

        return jsonify({'message': 'The widget was successfully deleted'}), 200

@bp.route('/clients_domains', methods=['GET'])
def get_all_clients_domains():
        installations = Installation.query.with_entities(Installation.client_domain).distinct().all()

        if not installations:
            return jsonify({'message': 'No clients domains found.'}), 404

        clients_domains = [{'client_domain': installation.client_domain} for installation in installations]

        return jsonify(clients_domains), 200

bp.route('/installations', methods=['DELETE'])
def delete_installation():
    data = request.get_json()
    client_domain = data.get('client_domain')
    id_widget = data.get('id_widget')

    if not client_domain or not id_widget:
        return jsonify({'error': 'You must specify the client_domain and id_widget.'}), 400

    installation = Installation.query.filter_by(client_domain=client_domain, id_widget=id_widget).first()

    if installation:
        db.session.delete(installation)
        db.session.commit()
        return jsonify({'message': 'Installation deleted successfully'}), 200
    else:
        return jsonify({'message': 'Installation not found'}), 404