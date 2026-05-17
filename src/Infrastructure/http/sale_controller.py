from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data_base import db
from src.Infrastructure.http.auth_utils import get_authenticated_seller, parse_quantity
from src.Infrastructure.Model.product import Product
from src.Infrastructure.Model.sale import Sale

sale_bp = Blueprint('sale_bp', __name__)


@sale_bp.route('/api/sales', methods=['GET'])
@jwt_required()
def list_sales():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    sales = Sale.query.filter_by(seller_id=seller.id).order_by(Sale.created_at.desc()).all()
    return jsonify({"sales": [s.to_dict() for s in sales]}), 200


@sale_bp.route('/api/sales/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    sale = Sale.query.filter_by(id=sale_id, seller_id=seller.id).first()
    if not sale:
        return jsonify({"error": "Venda nao encontrada"}), 404

    return jsonify({"sale": sale.to_dict()}), 200


@sale_bp.route('/api/sales', methods=['POST'])
@jwt_required()
def create_sale():
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    data = request.get_json() or {}
    product_id = parse_quantity(data.get('produtoId', data.get('produto_id')))
    quantity = parse_quantity(data.get('quantidade'))

    if product_id is None or quantity is None:
        return jsonify({"error": "Produto e quantidade sao obrigatorios"}), 400

    if product_id <= 0:
        return jsonify({"error": "Produto invalido"}), 400

    if quantity <= 0:
        return jsonify({"error": "Quantidade vendida deve ser maior que zero"}), 400

    product = Product.query.filter_by(id=product_id, seller_id=seller.id).first()

    if not product:
        return jsonify({"error": "Produto nao encontrado"}), 404

    if product.status != 'Ativo':
        return jsonify({"error": "Produtos inativados nao podem ser vendidos"}), 400

    if quantity > product.quantidade:
        return jsonify({"error": "Nao e possivel vender mais do que a quantidade em estoque"}), 400

    sale = Sale(
        seller_id=seller.id,
        product_id=product.id,
        quantidade_vendida=quantity,
        preco_produto_momento_venda=product.preco,
    )

    product.quantidade -= quantity

    db.session.add(sale)
    db.session.commit()

    return jsonify({
        "message": "Venda realizada com sucesso",
        "sale": sale.to_dict(),
        "product": product.to_dict(),
    }), 201


@sale_bp.route('/api/sales/<int:sale_id>', methods=['PUT'])
@jwt_required()
def update_sale(sale_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    sale = Sale.query.filter_by(id=sale_id, seller_id=seller.id).first()
    if not sale:
        return jsonify({"error": "Venda nao encontrada"}), 404

    data = request.get_json() or {}
    new_product_id = parse_quantity(data.get('produtoId', data.get('produto_id')))
    new_quantity = parse_quantity(data.get('quantidade'))

    if new_product_id == sale.product_id:
        new_product_id = None

    if new_product_id is None and new_quantity is None:
        return jsonify({"error": "Nenhum campo para atualizar"}), 400

    if new_quantity is not None and new_quantity <= 0:
        return jsonify({"error": "Quantidade vendida deve ser maior que zero"}), 400

    current_product = Product.query.filter_by(id=sale.product_id, seller_id=seller.id).first()

    if new_product_id is not None:
        if new_product_id <= 0:
            return jsonify({"error": "Produto invalido"}), 400

        new_product = Product.query.filter_by(id=new_product_id, seller_id=seller.id).first()
        if not new_product:
            return jsonify({"error": "Produto nao encontrado"}), 404

        if new_product.status != 'Ativo':
            return jsonify({"error": "Produtos inativados nao podem ser vendidos"}), 400

        qty_to_use = new_quantity if new_quantity is not None else sale.quantidade_vendida

        if qty_to_use > new_product.quantidade:
            return jsonify({"error": "Nao e possivel vender mais do que a quantidade em estoque"}), 400

        current_product.quantidade += sale.quantidade_vendida
        new_product.quantidade -= qty_to_use

        sale.product_id = new_product_id
        sale.quantidade_vendida = qty_to_use
        sale.preco_produto_momento_venda = new_product.preco

        updated_product = new_product
    else:
        if current_product.status != 'Ativo':
            return jsonify({"error": "Produto inativado nao pode ter venda editada"}), 400

        diff = new_quantity - sale.quantidade_vendida

        if diff > 0 and diff > current_product.quantidade:
            return jsonify({"error": "Nao e possivel vender mais do que a quantidade em estoque"}), 400

        current_product.quantidade -= diff
        sale.quantidade_vendida = new_quantity

        updated_product = current_product

    db.session.commit()

    return jsonify({
        "message": "Venda atualizada com sucesso",
        "sale": sale.to_dict(),
        "product": updated_product.to_dict(),
    }), 200


@sale_bp.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def cancel_sale(sale_id):
    seller, error_response = get_authenticated_seller()
    if error_response:
        return error_response

    sale = Sale.query.filter_by(id=sale_id, seller_id=seller.id).first()
    if not sale:
        return jsonify({"error": "Venda nao encontrada"}), 404

    product = Product.query.filter_by(id=sale.product_id, seller_id=seller.id).first()
    if product:
        product.quantidade += sale.quantidade_vendida

    db.session.delete(sale)
    db.session.commit()

    return jsonify({"message": "Venda cancelada e estoque restaurado com sucesso"}), 200
