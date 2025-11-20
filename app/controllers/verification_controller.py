from ..models.certificate import Certificate
from ..models.verification_log import VerificationLog
from ..extensions import db
from flask import request
from datetime import datetime

def verify_certificate(code):
    cert = Certificate.query.filter_by(verification_code=code, is_active=True).first()
    ip_address = request.remote_addr
    if cert:
        status = 'VALID'
    else:
        status = 'INVALID'

    log = VerificationLog(certificate_id=cert.id if cert else None,
                          verified_at=datetime.utcnow(),
                          ip_address=ip_address,
                          status=status)
    db.session.add(log)
    db.session.commit()

    return {
        "status": status,
        "certificate": {
            "student_name": cert.student_name if cert else None,
            "course_name": cert.course_name if cert else None,
            "verification_code": code
        }
    }
