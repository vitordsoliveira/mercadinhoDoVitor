from data_base import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    imagem = db.Column(db.String(255), nullable=True)

    sales = db.relationship('Sale', backref='product', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "nome": self.nome,
            "preco": round(float(self.preco), 2),
            "quantidade": self.quantidade,
            "status": self.status,
            "imagem": self.imagem,
        }
