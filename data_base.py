import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

db = SQLAlchemy()

def init_db(app):
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'mercadinho.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        run_sqlite_migrations()


def run_sqlite_migrations():
    inspector = inspect(db.engine)

    if 'sellers' not in inspector.get_table_names():
        return

    seller_columns = {column['name'] for column in inspector.get_columns('sellers')}

    if 'api_token' in seller_columns:
        return

    with db.engine.begin() as connection:
        connection.execute(text("ALTER TABLE sellers ADD COLUMN api_token VARCHAR(64)"))
