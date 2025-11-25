from ..extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(50), nullable=True)
    responsibility = db.Column(db.String(255), nullable=True)
    year_of_employment = db.Column(db.String(10), nullable=True)
    role = db.Column(db.String(50), default='admin')  # 'admin', 'student', 'employer'
    staff_id = db.Column(db.String(50), unique=True, nullable=True)  # auto generated
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"










# from ..extensions import db
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash

# class User(db.Model):
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password_hash = db.Column(db.String(255), nullable=False)
#     role = db.Column(db.String(50), default='admin')  # 'admin', 'student', 'employer'
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
