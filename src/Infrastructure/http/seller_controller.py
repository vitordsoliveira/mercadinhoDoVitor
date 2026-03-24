from flask import Blueprint, request, jsonify
from src.Infrastructure.Model.seller import Seller
from data_base import db
from src.Infrastructure.http.whats_app import send_activation_code
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
        send_activation_code(new_seller.celular, activation_code)

        db.session.commit()

        return jsonify({'message': 'Cadastro realizado! Verifique seu WhatsApp para o código de ativação.'}), 201

    except ValueError as e:
        db.session.rollback()
        print(f"DEBUG: Config Error - {e}")
        return jsonify({'error': str(e)}), 500
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


@seller_bp.route('/api/sellers/<int:seller_id>', methods=['PUT'])
def update_seller(seller_id):
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Nenhum dado enviado para atualização'}), 400

    seller = Seller.query.get(seller_id)

    if not seller:
        return jsonify({'error': 'Seller não encontrado'}), 404

    email = data.get('email', seller.email)
    cnpj = data.get('cnpj', seller.cnpj)
    celular = data.get('celular', seller.celular)

    if celular and not celular.startswith('+'):
        celular = f"+55{celular}"

    seller_with_same_email = Seller.query.filter(Seller.email == email, Seller.id != seller_id).first()
    seller_with_same_cnpj = Seller.query.filter(Seller.cnpj == cnpj, Seller.id != seller_id).first()
    seller_with_same_celular = Seller.query.filter(Seller.celular == celular, Seller.id != seller_id).first()

    if seller_with_same_email or seller_with_same_cnpj or seller_with_same_celular:
        return jsonify({'error': 'E-mail, CNPJ ou Celular já cadastrado para outro seller'}), 409

    seller.nome = data.get('nome', seller.nome)
    seller.email = email
    seller.cnpj = cnpj
    seller.celular = celular
    seller.status = data.get('status', seller.status)

    if data.get('senha'):
        seller.set_password(data['senha'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'Seller atualizado com sucesso',
            'seller': {
                'id': seller.id,
                'nome': seller.nome,
                'cnpj': seller.cnpj,
                'email': seller.email,
                'celular': seller.celular,
                'status': seller.status
            }
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"DEBUG: Database Error - {e}")
        return jsonify({'error': 'Ocorreu um erro interno ao atualizar os dados.'}), 500