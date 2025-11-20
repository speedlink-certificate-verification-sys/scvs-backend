from ..models.certificate import Certificate
from ..extensions import db
from ..utils.code_generator import generate_unique_code
from ..utils.pdf_generator import generate_certificate_pdf

def create_certificate(data):
    student_name = data.get('student_name')
    course_name = data.get('course_name')
    verification_code = generate_unique_code()

    pdf_path = generate_certificate_pdf(student_name, course_name, verification_code)

    cert = Certificate(
        student_name=student_name,
        course_name=course_name,
        verification_code=verification_code,
        pdf_url=pdf_path
    )
    db.session.add(cert)
    db.session.commit()

    return {
        "student_name": student_name,
        "course_name": course_name,
        "verification_code": verification_code,
        "pdf_url": pdf_path
    }
