from ..extensions import db
from datetime import datetime

class VerificationLog(db.Model):
    __tablename__ = 'verification_logs'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'))
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20))  # VALID / INVALID / EXPIRED

    certificate = db.relationship('Certificate', backref='verification_logs')
