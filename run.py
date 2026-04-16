import os
from datetime import timedelta

from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from data_base import init_db
from src.Infrastructure.http.auth_controller import auth_bp
from src.Infrastructure.http.product_controller import product_bp
from src.Infrastructure.http.sale_controller import sale_bp
from src.Infrastructure.http.seller_controller import seller_bp
from src.routes import init_routes


def create_app():
    app = Flask(__name__)

    load_dotenv(find_dotenv())

    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "15"))
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "30"))
    )
    JWTManager(app)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": os.getenv("CORS_ALLOWED_ORIGINS", "*"),
                "allow_headers": ["Content-Type", "Authorization"],
                "methods": ["GET", "POST", "PUT", "PATCH", "OPTIONS"],
            }
        },
    )

    init_db(app)
    init_routes(app)

    app.register_blueprint(seller_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(sale_bp)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port=3223)
