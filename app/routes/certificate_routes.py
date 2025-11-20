from flask import Blueprint, request, jsonify
from ..controllers.certificate_controller import create_certificate

certificate_bp = Blueprint('certificate_bp', __name__, url_prefix='/certificate')

@certificate_bp.post('/create')
def create_cert():
    data = request.json
    result = create_certificate(data)
    return jsonify(result)
