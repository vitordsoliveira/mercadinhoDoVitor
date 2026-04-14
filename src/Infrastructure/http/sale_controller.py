from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data_base import db
from src.Infrastructure.http.auth_utils import get_authenticated_seller, parse_quantity
from src.Infrastructure.Model.product import Product
from src.Infrastructure.Model.sale import Sale

sale_bp = Blueprint('sale_bp', __name__)


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
