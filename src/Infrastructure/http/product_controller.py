from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data_base import db
from src.Infrastructure.http.auth_utils import (
    ALLOWED_PRODUCT_STATUSES,
    ACTIVE_STATUS,
    get_authenticated_seller,
    parse_price,
    parse_quantity,
)
from src.Infrastructure.Model.product import Product

product_bp = Blueprint('product_bp', __name__)


def _find_owned_product(product_id, seller_id):
    return Product.query.filter_by(id=product_id, seller_id=seller_id).first()


def _validate_product_payload(data, partial=False):
    if not data:
        return None, (jsonify({"error": "Payload invalido"}), 400)

    payload = {}
    required_fields = ['nome', 'preco', 'quantidade']

    if not partial:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return None, (jsonify({"error": f"Campos obrigatorios ausentes: {', '.join(missing_fields)}"}), 400)

    if 'nome' in data:
        nome = str(data.get('nome') or '').strip()
        if not nome:
            return None, (jsonify({"error": "Nome do produto e obrigatorio"}), 400)
        payload['nome'] = nome

    if 'preco' in data:
        preco = parse_price(data.get('preco'))
        if preco is None:
            return None, (jsonify({"error": "Preco invalido"}), 400)
        payload['preco'] = preco

    if 'quantidade' in data:
        quantidade = parse_quantity(data.get('quantidade'))
        if quantidade is None or quantidade < 0:
            return None, (jsonify({"error": "Quantidade invalida"}), 400)
        payload['quantidade'] = quantidade

    if 'status' in data:
        status = str(data.get('status') or '').strip()
        if status not in ALLOWED_PRODUCT_STATUSES:
            return None, (jsonify({"error": "Status invalido. Use Ativo ou Inativo"}), 400)
        payload['status'] = status
    elif not partial:
        payload['status'] = ACTIVE_STATUS

    if 'imagem' in data or 'img' in data:
        imagem = data.get('imagem', data.get('img'))
        if imagem is not None and not isinstance(imagem, str):
            return None, (jsonify({"error": "Imagem invalida"}), 400)
        payload['imagem'] = imagem.strip() if isinstance(imagem, str) else imagem
    elif not partial:
        payload['imagem'] = None

    if partial and not payload:
        return None, (jsonify({"error": "Nenhum campo valido informado para atualizacao"}), 400)

    return payload, None


@product_bp.route('/api/products', methods=['POST'])
@jwt_required()
def create_product():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    payload, error_response = _validate_product_payload(request.get_json() or {})
    if error_response:
        return error_response

    product = Product(seller_id=seller.id, **payload)
    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Produto cadastrado com sucesso",
        "product": product.to_dict(),
    }), 201


@product_bp.route('/api/products', methods=['GET'])
@jwt_required()
def list_products():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    products = Product.query.filter_by(seller_id=seller.id).order_by(Product.id.desc()).all()

    return jsonify({
        "products": [product.to_dict() for product in products],
    }), 200


@product_bp.route('/api/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    product = _find_owned_product(product_id, seller.id)
    if not product:
        return jsonify({"error": "Produto nao encontrado"}), 404

    return jsonify({"product": product.to_dict()}), 200


@product_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    product = _find_owned_product(product_id, seller.id)
    if not product:
        return jsonify({"error": "Produto nao encontrado"}), 404

    payload, error_response = _validate_product_payload(request.get_json() or {}, partial=True)
    if error_response:
        return error_response

    for field_name, field_value in payload.items():
        setattr(product, field_name, field_value)

    db.session.commit()

    return jsonify({
        "message": "Produto atualizado com sucesso",
        "product": product.to_dict(),
    }), 200


@product_bp.route('/api/products/<int:product_id>/inactivate', methods=['PATCH'])
@jwt_required()
def inactivate_product(product_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    product = _find_owned_product(product_id, seller.id)
    if not product:
        return jsonify({"error": "Produto nao encontrado"}), 404

    product.status = 'Inativo'
    db.session.commit()

    return jsonify({
        "message": "Produto inativado com sucesso",
        "product": product.to_dict(),
    }), 200
