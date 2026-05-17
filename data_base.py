import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()

def init_db(app):
    database_url = os.getenv('DATABASE_URL', '')

    if database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)

    if not database_url:
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'mercadinho.db')
        database_url = f'sqlite:///{db_path}'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        run_migrations()


def run_migrations():
    inspector = inspect(db.engine)

    if 'sellers' not in inspector.get_table_names():
        return

    seller_columns = {column['name'] for column in inspector.get_columns('sellers')}

    if 'api_token' not in seller_columns:
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE sellers ADD COLUMN api_token VARCHAR(64)"))

    if 'sales' not in inspector.get_table_names():
        return

    sale_columns = {column['name'] for column in inspector.get_columns('sales')}

    if 'created_at' not in sale_columns:
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE sales ADD COLUMN created_at DATETIME"))

    if 'products' not in inspector.get_table_names():
        return

    product_columns = {col['name']: col for col in inspector.get_columns('products')}
    imagem_col = product_columns.get('imagem')
    if imagem_col and hasattr(imagem_col['type'], 'length') and imagem_col['type'].length == 255:
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE products MODIFY COLUMN imagem MEDIUMTEXT"))
