from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from data_base import db
from src.Infrastructure.Model.seller import Seller

ACTIVE_STATUS = 'Ativo'
INACTIVE_STATUS = 'Inativo'
ALLOWED_PRODUCT_STATUSES = {ACTIVE_STATUS, INACTIVE_STATUS}


def normalize_phone_number(phone_number):
    normalized_phone_number = str(phone_number or '').strip()

    if not normalized_phone_number:
        return normalized_phone_number

    if normalized_phone_number.startswith('+'):
        return normalized_phone_number

    return f"+55{normalized_phone_number}"


def get_authenticated_seller(require_active=True):
    seller_id = get_jwt_identity()

    try:
        seller_id = int(seller_id)
    except (TypeError, ValueError):
        return None, (jsonify({"error": "Token invalido"}), 401)

    seller = db.session.get(Seller, seller_id)

    if not seller:
        return None, (jsonify({"error": "Seller nao encontrado"}), 404)

    if require_active and seller.status != ACTIVE_STATUS:
        return None, (jsonify({"error": "Seller inativo nao pode executar esta acao"}), 403)

    return seller, None


def parse_quantity(value):
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())

    return None


def parse_price(value):
    if value is None or isinstance(value, bool):
        return None

    try:
        price = round(float(value), 2)
    except (TypeError, ValueError):
        return None

    if price < 0:
        return None

    return price
