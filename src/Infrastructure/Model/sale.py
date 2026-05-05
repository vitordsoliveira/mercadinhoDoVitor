from datetime import datetime, timezone

from data_base import db


class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantidade_vendida = db.Column(db.Integer, nullable=False)
    preco_produto_momento_venda = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        preco_unitario = round(float(self.preco_produto_momento_venda), 2)
        produto = self.product

        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "produto_id": self.product_id,
            "quantidade": self.quantidade_vendida,
            "preco_produto_momento_venda": preco_unitario,
            "valor_total": round(preco_unitario * self.quantidade_vendida, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "imagem": produto.imagem,
            } if produto else None,
        }
