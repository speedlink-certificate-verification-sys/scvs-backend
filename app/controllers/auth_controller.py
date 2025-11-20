from ..models.user import User
from ..extensions import db
from flask_jwt_extended import create_access_token
from flask import jsonify, request

def register_user(data):
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')

    if User.query.filter_by(email=email).first():
        return {"message": "User already exists"}, 400

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}

def login_user(data):
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"access_token": token}
    else:
        return {"message": "Invalid credentials"}, 401
