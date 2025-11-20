from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import register_user, login_user
from flasgger import swag_from

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.post('/register')
@swag_from({
    "tags": ["Auth"],
    "parameters": [
        {"name": "email", "in": "formData", "type": "string", "required": True},
        {"name": "password", "in": "formData", "type": "string", "required": True},
        {"name": "role", "in": "formData", "type": "string", "required": False}
    ],
    "responses": {200: {"description": "User registered successfully"}}
})
def register():
    data = request.json
    result = register_user(data)
    return jsonify(result)

@auth_bp.post('/login')
@swag_from({
    "tags": ["Auth"],
    "parameters": [
        {"name": "email", "in": "formData", "type": "string", "required": True},
        {"name": "password", "in": "formData", "type": "string", "required": True}
    ],
    "responses": {200: {"description": "Login successful"}}
})
def login():
    data = request.json
    result = login_user(data)
    return jsonify(result)
