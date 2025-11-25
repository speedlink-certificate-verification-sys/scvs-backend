from ..models.user import User
from ..extensions import db
from flask_jwt_extended import create_access_token
from flask import jsonify, request
from ..utils.staff_id_generator import generate_staff_id



# def register_user(data):
#     email = data.get('email')
#     password = data.get('password')
#     role = data.get('role', 'admin')

#     if User.query.filter_by(email=email).first():
#         return {"message": "User already exists"}, 400

#     user = User(email=email, role=role)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()

#     return {"message": "User registered successfully"}


def register_user(data):
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    responsibility = data.get('responsibility')
    year_of_employment = data.get('year_of_employment')

    if User.query.filter_by(email=email).first():
        return {"message": "User already exists"}, 400

    staff_id = generate_staff_id(role=role, year_of_employment=year_of_employment)

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        responsibility=responsibility,
        year_of_employment=year_of_employment,
        role=role,
        staff_id=staff_id
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User registered successfully",
        "staff_id": staff_id
    }


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"access_token": token}
    else:
        return {"message": "Invalid credentials"}, 401
