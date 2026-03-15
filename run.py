from flask import Flask
from flask_jwt_extended import JWTManager
from data_base import init_db
from src.routes import init_routes
from src.Infrastructure.http.seller_controller import seller_bp
from src.Infrastructure.http.auth_controller import auth_bp
import os
from dotenv import load_dotenv, find_dotenv

def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'uma-chave-secreta-para-funfar-:D')

    init_db(app)
    init_routes(app)

    app.register_blueprint(seller_bp)
    app.register_blueprint(auth_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=3223)
