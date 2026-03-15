import os
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from data_base import init_db
from Infrastructure.http.seller_controller import seller_bp
from Infrastructure.http.auth_controller import auth_bp

def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')

    init_db(app)
    jwt = JWTManager(app)

    app.register_blueprint(seller_bp)
    app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)