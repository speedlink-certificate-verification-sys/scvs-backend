from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes import register_routes
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Flasgger
    Swagger(app)

    register_routes(app)
    return app
