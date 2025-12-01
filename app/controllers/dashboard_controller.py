# dashboard_controller.py
from ..models.certificate import Certificate
from ..models.verification_log import VerificationLog
from ..models.user import User
from ..extensions import db
from sqlalchemy import func
from flask import request
from sqlalchemy.orm import joinedload


def dashboard_summary():
    try:
        # Metrics
        total_certs = Certificate.query.count()
        total_verified_certs = VerificationLog.query.filter_by(status="VALID").count()
        
        # Query Student table
        from ..models.student import Student
        total_students = Student.query.count()

        # Get certificates that have been verified at least once
        verified_certificate_ids = db.session.query(VerificationLog.certificate_id).filter(
            VerificationLog.status == "VALID"
        ).distinct()
        
        # Pending = total certificates - verified certificates
        pending_verifications = total_certs - verified_certificate_ids.count()

        courses_managed = db.session.query(func.count(func.distinct(Certificate.course_name))).scalar()

        # Recent verifications with student names
        recent_logs = (
            VerificationLog.query
            .options(joinedload(VerificationLog.certificate))
            .filter(VerificationLog.certificate_id.isnot(None))
            .order_by(VerificationLog.verified_at.desc())
            .limit(50)
            .all()
        )

        # Filter to get only the most recent verification for each certificate code
        seen_codes = set()
        recent_verifications = []
        
        for log in recent_logs:
            if log.certificate and log.certificate.verification_code not in seen_codes:
                seen_codes.add(log.certificate.verification_code)
                recent_verifications.append({
                    "name": f"{log.certificate.student_first_name} {log.certificate.student_last_name}",
                    "course": log.certificate.course_name,
                    "date_verified": log.verified_at.strftime("%Y-%m-%d %H:%M") if log.verified_at else None,
                    "status": log.status,
                    "certificate_code": log.certificate.verification_code
                })
                
                # Stop when we have 10 unique certificates
                if len(recent_verifications) >= 10:
                    break
        # recent_verifications = []
        # for log in recent_logs:
        #     if log.certificate:
        #         recent_verifications.append({
        #             "name": f"{log.certificate.student_first_name} {log.certificate.student_last_name}",
        #             "course": log.certificate.course_name,
        #             "date_verified": log.verified_at.strftime("%Y-%m-%d %H:%M") if log.verified_at else None,
        #             "status": log.status,
        #             "certificate_code": log.certificate.verification_code
        #         })

        return {
            "metrics": {
                "total_certificates": total_certs,
                "total_verified_certificates": total_verified_certs,
                "total_students": total_students,
                "pending_verifications": pending_verifications,
                "courses_managed": courses_managed
            },
            "recent_verifications": recent_verifications
        }

    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "metrics": {
                "total_certificates": 0,
                "total_verified_certificates": 0,
                "total_students": 0,
                "pending_verifications": 0,
                "courses_managed": 0
            },
            "recent_verifications": [],
            "error": str(e)
        }
    

def certificates_table():
    # Remove pagination parameters
    all_certificates = Certificate.query.order_by(Certificate.issued_at.desc()).all()

    data = [
        {
            "id": cert.id,
            "name": f"{cert.student_first_name} {cert.student_last_name}",
            "course": cert.course_name,
            "certificate_code": cert.verification_code,
            "issued_at": cert.issued_at.strftime("%Y-%m-%d") if cert.issued_at else None,
            "student_id": cert.student_id
        }
        for cert in all_certificates
    ]

    return {
        "certificates": data,
        "count": len(data)
    }

# def certificates_table(page=1, per_page=10):
#     try:
#         page = request.args.get('page', page, type=int)
#         per_page = request.args.get('per_page', per_page, type=int)

#         pagination = (
#             Certificate.query
#             .order_by(Certificate.issued_at.desc())
#             .paginate(page=page, per_page=per_page, error_out=False)
#         )

#         data = [
#             {
#                 "id": cert.id,
#                 "name": f"{cert.student_first_name} {cert.student_last_name}",  # FIX: Combine first and last name
#                 "course": cert.course_name,
#                 "certificate_code": cert.verification_code,
#                 "issued_at": cert.issued_at.strftime("%Y-%m-%d") if cert.issued_at else None,
#                 "student_id": cert.student_id
#             }
#             for cert in pagination.items
#         ]

#         return {
#             "certificates": data,
#             "pagination": {
#                 "page": pagination.page,
#                 "per_page": pagination.per_page,
#                 "total_pages": pagination.pages,
#                 "total_items": pagination.total
#             }
#         }
#     except Exception as e:
#         print(f"Certificates table error: {str(e)}")
#         return {
#             "certificates": [],
#             "pagination": {
#                 "page": 1,
#                 "per_page": per_page,
#                 "total_pages": 0,
#                 "total_items": 0
#             },
#             "error": str(e)
#         }
