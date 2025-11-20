from .certificate_routes import certificate_bp
from .verification_routes import verification_bp
from .auth_routes import auth_bp

def register_routes(app):
    app.register_blueprint(certificate_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(auth_bp)
