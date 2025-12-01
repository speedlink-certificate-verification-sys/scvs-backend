from ..models.certificate import Certificate
from ..models.verification_log import VerificationLog
from ..extensions import db
from flask import request
from datetime import datetime



def verify_certificate(code):
    try:
        # FIX: Remove is_active filter since it doesn't exist in your model
        cert = Certificate.query.filter_by(
            verification_code=code
            # Remove: is_active=True - this field doesn't exist in your Certificate model
        ).first()

        ip = request.remote_addr
        status = "VALID" if cert else "INVALID"

        # Log attempt
        log = VerificationLog(
            certificate_id=cert.id if cert else None,
            verified_at=datetime.utcnow(),
            ip_address=ip,
            status=status
        )
        db.session.add(log)
        db.session.commit()

        if not cert:
            return {
                "status": "INVALID",
                "message": "Certificate not found"
            }

        return {
            "status": "VALID",
            "certificate": {
                "student_name": f"{cert.student_first_name} {cert.student_last_name}",
                "course_name": cert.course_name,
                "verification_code": cert.verification_code,
                "issued_at": cert.issued_at.strftime("%Y-%m-%d") if cert.issued_at else None,
                "qr_code_url": cert.qr_code_url,
                "year_of_study": cert.year_of_study,
                "course_summary": cert.course_summary
            }
        }

    except Exception as e:
        db.session.rollback()
        # Print the error for debugging
        print(f"Verification error: {str(e)}")
        return {
            "status": "ERROR",
            "message": f"Verification failed: {str(e)}"
        }, 500
    







# from ..models.certificate import Certificate
# from ..models.verification_log import VerificationLog
# from ..extensions import db
# from flask import request
# from datetime import datetime

# def verify_certificate(code):
#     cert = Certificate.query.filter_by(verification_code=code, is_active=True).first()
#     ip_address = request.remote_addr
#     if cert:
#         status = 'VALID'
#     else:
#         status = 'INVALID'

#     log = VerificationLog(certificate_id=cert.id if cert else None,
#                           verified_at=datetime.utcnow(),
#                           ip_address=ip_address,
#                           status=status)
#     db.session.add(log)
#     db.session.commit()

#     return {
#         "status": status,
#         "certificate": {
#             "student_name": cert.student_name if cert else None,
#             "course_name": cert.course_name if cert else None,
#             "verification_code": code
#         }
#     }
