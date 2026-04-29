from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from data_base import db
from src.Infrastructure.Model.seller import Seller

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login_seller():
    data = request.get_json() or {}

    if not data.get('email') or not data.get('senha'):
        return jsonify({"error": "E-mail e senha sao obrigatorios"}), 400

    seller = Seller.query.filter_by(email=data.get('email')).first()

    if not seller or not seller.check_password(data.get('senha')):
        return jsonify({"error": "Credenciais invalidas"}), 401

    if seller.status != 'Ativo':
        return jsonify({"error": "Sua conta nao esta ativa, ative primeiro"}), 403

    provided_token = data.get('token', '').strip()

    if provided_token and seller.api_token and seller.api_token != provided_token:
        return jsonify({"error": "Token do seller invalido"}), 401

    token_regenerated = not provided_token
    if token_regenerated or not seller.api_token:
        seller.generate_api_token()
        db.session.commit()

    access_token = create_access_token(identity=str(seller.id))

    response_data = {
        "access_token": access_token,
        "seller": seller.to_dict(include_token=True),
    }

    if token_regenerated:
        response_data["message"] = "Token gerado para a conta. Guarde-o para os proximos logins."

    return jsonify(response_data), 200
