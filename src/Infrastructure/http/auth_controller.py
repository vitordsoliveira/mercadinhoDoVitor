from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from src.Infrastructure.Model.seller import Seller

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login_seller():
    data = request.get_json()

    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    email = data.get('email')
    password = data.get('senha')

    seller = Seller.query.filter_by(email=email).first()

    if not seller or not seller.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    if seller.status != 'Ativo':
        return jsonify({"error": "Sua conta não está ativa, ative!"}), 403

    access_token = create_access_token(identity=seller.id)
    
    return jsonify(access_token=access_token), 200