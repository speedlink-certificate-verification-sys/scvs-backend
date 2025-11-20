from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, jwt
from .routes import register_routes
from flasgger import Swagger
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app)

    # Flasgger
    # Swagger(app)

    # --------------------------------------------------------
    # SWAGGER TEMPLATE (BRANDED)
    # --------------------------------------------------------
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Speedlink Certificate Verification API",
            "description": "API documentation for the Speedlink Certificate Verification & Dashboard System.",
            "version": "1.0.0",
            "contact": {
                "name": "Speedlink Engineering Team",
                "url": "https://speedlinkng.com",
            },
        },
        "basePath": "/",  # Root path
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT token: **Bearer <token>**"
            }
        }
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"     # Swagger UI will be here
    }

    Swagger(app, template=swagger_template, config=swagger_config)


     # Base URL route — quick server check
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "status": "live",
            "message": "PARADOX backend running successfully on Speedlink server!",
            "info": "All systems nominal. Visit /api/* endpoints to interact."
        })

    register_routes(app)
    return app
