# dashboard_controller.py
from ..models.certificate import Certificate
from ..models.verification_log import VerificationLog
from ..models.user import User
from ..extensions import db
from sqlalchemy import func
from flask import request
from sqlalchemy.orm import joinedload



def dashboard_summary():
    # Metrics
    total_certs = Certificate.query.count()
    total_verified_certs = VerificationLog.query.filter_by(status="VALID").count()
    total_students = User.query.filter_by(role="student").count()

    # Pending certificates (no verification logs)
    pending_verifications = Certificate.query.outerjoin(VerificationLog).filter(VerificationLog.id.is_(None)).count()

    courses_managed = db.session.query(func.count(func.distinct(Certificate.course_name))).scalar()

    # Optimized query: eager load certificates
    recent_logs = (
        VerificationLog.query
        .options(joinedload(VerificationLog.certificate))
        .order_by(VerificationLog.verified_at.desc())
        .limit(10)
        .all()
    )

    recent_verifications = [
        {
            "name": log.certificate.student_name if log.certificate else None,
            "course": log.certificate.course_name if log.certificate else None,
            "date_verified": log.verified_at,
            "status": log.status
        }
        for log in recent_logs
    ]

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


def certificates_table(page=1, per_page=10):
    page = request.args.get('page', page, type=int)
    per_page = request.args.get('per_page', per_page, type=int)

    pagination = (
        Certificate.query
        .order_by(Certificate.issued_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    data = [
        {
            "id": cert.id,
            "name": cert.student_name,
            "course": cert.course_name,
            "certificate_code": cert.verification_code,
            "issued_at": cert.issued_at
        }
        for cert in pagination.items
    ]

    return {
        "certificates": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total
        }
    }







