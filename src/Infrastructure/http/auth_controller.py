from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from data_base import db
from src.Infrastructure.Model.seller import Seller

auth_bp = Blueprint('auth_bp', __name__)


def _build_auth_response(seller, include_message=False):
    response_data = {
        "access_token": create_access_token(identity=str(seller.id)),
        "refresh_token": create_refresh_token(identity=str(seller.id)),
        "seller": seller.to_dict(include_token=True),
    }

    if include_message:
        response_data["message"] = "Token gerado para a conta. Use este token nos proximos logins."

    return response_data


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

    if not seller.api_token:
        seller.generate_api_token()
        db.session.commit()
    elif seller.api_token != data.get('token'):
        return jsonify({"error": "Token do seller invalido"}), 401

    return jsonify(
        _build_auth_response(seller, include_message=not data.get('token'))
    ), 200


@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_seller_session():
    seller_id = get_jwt_identity()

    try:
        seller_id = int(seller_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Token invalido"}), 401

    seller = db.session.get(Seller, seller_id)

    if not seller:
        return jsonify({"error": "Seller nao encontrado"}), 404

    if seller.status != 'Ativo':
        return jsonify({"error": "Seller inativo nao pode renovar a sessao"}), 403

    return jsonify(_build_auth_response(seller)), 200
