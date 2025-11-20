from ..extensions import db
from datetime import datetime

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_code = db.Column(db.String(100), unique=True, nullable=False)
    pdf_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Certificate {self.verification_code}>"
