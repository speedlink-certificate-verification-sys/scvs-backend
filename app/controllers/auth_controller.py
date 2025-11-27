from ..models.user import User
from ..extensions import db
from flask_jwt_extended import create_access_token
from flask import jsonify, request
from ..utils.staff_id_generator import generate_staff_id


def register_user(data):
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    responsibility = data.get('responsibility')
    year_of_employment = data.get('year_of_employment')

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return {"message": "User with this email already exists"}, 400

    # Generate a unique staff_id
    staff_id = generate_staff_id(role=role, year_of_employment=year_of_employment)
    
    # Ensure staff_id is unique
    max_attempts = 10
    attempts = 0
    while User.query.filter_by(staff_id=staff_id).first() and attempts < max_attempts:
        staff_id = generate_staff_id(role=role, year_of_employment=year_of_employment)
        attempts += 1
    
    if attempts == max_attempts:
        return {"message": "Unable to generate unique staff ID. Please try again."}, 500

    # Create and save user
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

    try:
        db.session.add(user)
        db.session.commit()
        
        return {
            "message": "User registered successfully",
            "staff_id": staff_id
        }, 201
        
    except Exception as e:
        db.session.rollback()
        return {"message": f"Registration failed: {str(e)}"}, 500


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"access_token": token}
    else:
        return {"message": "Invalid credentials"}, 401
