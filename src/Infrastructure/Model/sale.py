from data_base import db


class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantidade_vendida = db.Column(db.Integer, nullable=False)
    preco_produto_momento_venda = db.Column(db.Float, nullable=False)

    def to_dict(self):
        preco_unitario = round(float(self.preco_produto_momento_venda), 2)

        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "produto_id": self.product_id,
            "quantidade_vendida": self.quantidade_vendida,
            "preco_produto_momento_venda": preco_unitario,
            "valor_total": round(preco_unitario * self.quantidade_vendida, 2),
        }
