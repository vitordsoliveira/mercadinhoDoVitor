import random

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from twilio.base.exceptions import TwilioRestException

from data_base import db
from src.Infrastructure.http.auth_utils import get_authenticated_seller, normalize_phone_number
from src.Infrastructure.http.whats_app import send_activation_code
from src.Infrastructure.Model.seller import Seller

seller_bp = Blueprint('seller_bp', __name__)


@seller_bp.route('/api/sellers', methods=['POST'])
def create_seller():
    data = request.get_json() or {}

    if not all(field in data for field in ['nome', 'cnpj', 'email', 'celular', 'senha']):
        return jsonify({'error': 'Dados incompletos'}), 400

    celular = normalize_phone_number(data['celular'])

    if Seller.query.filter(
        (Seller.email == data['email']) |
        (Seller.cnpj == data['cnpj']) |
        (Seller.celular == celular)
    ).first():
        return jsonify({'error': 'E-mail, CNPJ ou celular ja cadastrado'}), 409

    activation_code = str(random.randint(1000, 9999))

    new_seller = Seller(
        nome=data['nome'],
        cnpj=data['cnpj'],
        email=data['email'],
        celular=celular,
        status='Inativo',
        activation_code=activation_code,
    )
    new_seller.set_password(data['senha'])

    try:
        db.session.add(new_seller)
        send_activation_code(new_seller.celular, activation_code)
        db.session.commit()

        return jsonify({
            'message': 'Cadastro realizado. Verifique seu WhatsApp para o codigo de ativacao.',
            'seller': new_seller.to_dict(),
        }), 201
    except ValueError as error:
        db.session.rollback()
        print(f"DEBUG: Config Error - {error}")
        return jsonify({'error': str(error)}), 500
    except TwilioRestException as error:
        db.session.rollback()
        print(f"DEBUG: Twilio API Error - {error}")
        return jsonify({
            'error': 'Falha ao enviar o codigo de ativacao. Verifique se o numero de celular esta correto e em formato internacional (+55119...).'
        }), 500
    except SQLAlchemyError as error:
        db.session.rollback()
        print(f"DEBUG: Database Error - {error}")
        return jsonify({'error': 'Ocorreu um erro interno ao salvar os dados.'}), 500


@seller_bp.route('/api/sellers/activate', methods=['POST'])
def activate_seller():
    data = request.get_json() or {}

    if not all(field in data for field in ['celular', 'codigo']):
        return jsonify({'error': 'Celular e codigo sao obrigatorios'}), 400

    celular = normalize_phone_number(data['celular'])
    seller = Seller.query.filter_by(celular=celular).first()

    if not seller:
        return jsonify({'error': 'Seller nao encontrado'}), 404

    if seller.status == 'Ativo':
        return jsonify({
            'message': 'Esta conta ja esta ativa. Use o token recebido na ativacao para fazer login.'
        }), 200

    if seller.activation_code != data['codigo']:
        return jsonify({'error': 'Codigo de ativacao invalido'}), 400

    seller.status = 'Ativo'
    seller.activation_code = None
    seller.generate_api_token()
    db.session.commit()

    access_token = create_access_token(identity=str(seller.id))

    return jsonify({
        'message': 'Conta ativada com sucesso.',
        'token': seller.api_token,
        'access_token': access_token,
        'seller': seller.to_dict(),
    }), 200


@seller_bp.route('/api/sellers/me', methods=['GET'])
@jwt_required()
def get_profile():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    return jsonify({'seller': seller.to_dict(include_token=True)}), 200


@seller_bp.route('/api/sellers/me', methods=['PUT'])
@jwt_required()
def update_profile():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    data = request.get_json() or {}
    updated = False

    if 'nome' in data:
        nome = str(data['nome'] or '').strip()
        if not nome:
            return jsonify({'error': 'Nome nao pode ser vazio'}), 400
        seller.nome = nome
        updated = True

    if 'email' in data:
        email = str(data['email'] or '').strip()
        if not email:
            return jsonify({'error': 'Email nao pode ser vazio'}), 400
        conflict = Seller.query.filter(Seller.email == email, Seller.id != seller.id).first()
        if conflict:
            return jsonify({'error': 'Email ja cadastrado'}), 409
        seller.email = email
        updated = True

    if 'celular' in data:
        celular = normalize_phone_number(data['celular'])
        conflict = Seller.query.filter(Seller.celular == celular, Seller.id != seller.id).first()
        if conflict:
            return jsonify({'error': 'Celular ja cadastrado'}), 409
        seller.celular = celular
        updated = True

    if 'senha' in data:
        senha = str(data['senha'] or '')
        if not senha:
            return jsonify({'error': 'Senha nao pode ser vazia'}), 400
        seller.set_password(senha)
        updated = True

    if not updated:
        return jsonify({'error': 'Nenhum campo para atualizar'}), 400

    db.session.commit()

    return jsonify({
        'message': 'Perfil atualizado com sucesso',
        'seller': seller.to_dict(include_token=True),
    }), 200
