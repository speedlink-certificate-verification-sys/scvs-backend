from flask import Blueprint, jsonify
from ..controllers.verification_controller import verify_certificate

verification_bp = Blueprint('verification_bp', __name__, url_prefix='/certificate')

@verification_bp.get('/<code>')
def verify(code):
    result = verify_certificate(code)
    return jsonify(result)
