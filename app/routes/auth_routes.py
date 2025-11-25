from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import register_user, login_user
from flasgger import swag_from


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# -------------------------
# REGISTER
# -------------------------
@auth_bp.post('/register')
@swag_from({
    "tags": ["Auth"],
    "summary": "Register a new admin",
    "description": "Creates a new admin account with staff ID generation.",
    "consumes": ["application/json"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "responsibility": {"type": "string"},
                    "year_of_employment": {"type": "string"},
                    "role": {"type": "string"}
                },
                "required": ["first_name", "last_name", "email", "password", "year_of_employment"]
            }
        }
    ],
    "responses": {
        "200": {"description": "User registered successfully"},
        "400": {"description": "Validation error / User exists"}
    }
})
def register():
    data = request.json
    result = register_user(data)
    return jsonify(result)


@auth_bp.post('/login')
@swag_from({
    "tags": ["Auth"],
    "summary": "Login a user",
    "description": "Authenticates a user with email and password and returns a JWT token.",
    "consumes": ["application/json"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["email", "password"]
            }
        }
    ],
    "responses": {
        "200": {"description": "Login successful"},
        "401": {"description": "Invalid credentials"}
    }
})
def login():
    data = request.json
    result = login_user(data)
    return jsonify(result)
