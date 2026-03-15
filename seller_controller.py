from flask import Blueprint, request, jsonify
from seller_model import Seller
from data_base import db
from twilio_service import send_activation_code
import random
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.exc import SQLAlchemyError

seller_bp = Blueprint('seller_bp', __name__)

@seller_bp.route('/api/sellers', methods=['POST'])
def create_seller():
    data = request.get_json()

    if not all(k in data for k in ['nome', 'cnpj', 'email', 'celular', 'senha']):
        return jsonify({'error': 'Dados incompletos'}), 400

    celular = data['celular']
    if not celular.startswith('+'):
        celular = f"+55{celular}"

    if Seller.query.filter((Seller.email == data['email']) | (Seller.cnpj == data['cnpj']) | (Seller.celular == celular)).first():
        return jsonify({'error': 'E-mail, CNPJ ou Celular já cadastrado'}), 409

    activation_code = str(random.randint(1000, 9999))

    new_seller = Seller(
        nome=data['nome'],
        cnpj=data['cnpj'],
        email=data['email'],
        celular=celular,
        status='Inativo',
        activation_code=activation_code
    )
    new_seller.set_password(data['senha'])

    try:
        db.session.add(new_seller)
        db.session.commit()

        send_activation_code(new_seller.celular, activation_code)

        return jsonify({'message': 'Cadastro realizado! Verifique seu WhatsApp para o código de ativação.'}), 201

    except TwilioRestException as e:
        db.session.rollback()
        print(f"DEBUG: Twilio API Error - {e}")
        return jsonify({'error': 'Falha ao enviar o código de ativação. Verifique se o número de celular está correto e em formato internacional (+55119...).'}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"DEBUG: Database Error - {e}")
        return jsonify({'error': 'Ocorreu um erro interno ao salvar os dados.'}), 500

@seller_bp.route('/api/sellers/activate', methods=['POST'])
def activate_seller():
    data = request.get_json()

    if not all(k in data for k in ['celular', 'codigo']):
        return jsonify({'error': 'Celular e código são obrigatórios'}), 400

    celular = data['celular']
    if not celular.startswith('+'):
        celular = f"+55{celular}"

    seller = Seller.query.filter_by(celular=celular).first()

    if not seller:
        return jsonify({'error': 'Seller não encontrado'}), 404

    if seller.status == 'Ativo':
        return jsonify({'message': 'Esta conta já está ativa'}), 200

    if seller.activation_code == data['codigo']:
        seller.status = 'Ativo'
        seller.activation_code = None 
        db.session.commit()
        return jsonify({'message': 'Conta ativada com sucesso!'}), 200
    else:
        return jsonify({'error': 'Código de ativação inválido'}), 400