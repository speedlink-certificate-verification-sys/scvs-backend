from flask import request, jsonify
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.certificate import Certificate
from ..utils.certificate_number import generate_certificate_number
from ..utils.qr_generator import generate_certificate_qr
import csv
from io import StringIO


# ===================================
# CREATE CERTIFICATE
# ===================================
def create_certificate():
    data = request.get_json()

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    course_name = data.get("course_name")
    course_summary = data.get("course_summary")
    year_of_study = data.get("year_of_study")
    issuance_date = data.get("issuance_date")  # frontend controls this

    # Generate cert number (course code is optional now)
    certificate_number = generate_certificate_number(course_name)

    # Generate QR
    qr_path = generate_certificate_qr(
        f"{first_name} {last_name}",
        course_name,
        certificate_number,
        issuance_date
    )

    cert = Certificate(
        student_first_name=first_name,
        student_last_name=last_name,
        course_name=course_name,
        course_summary=course_summary,
        year_of_study=year_of_study,
        verification_code=certificate_number,
        qr_code_url=qr_path,
        issued_at=issuance_date,
    )

    db.session.add(cert)
    db.session.commit()

    return jsonify({
        "message": "Certificate created successfully",
        "certificate_number": certificate_number,
    }), 201


# ===================================
# PAGINATED LIST (Optimized, no N+1)
# ===================================
def list_certificates():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    query = Certificate.query.order_by(Certificate.created_at.desc())

    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "items": [
            {
                "id": c.id,
                "student_name": f"{c.student_first_name} {c.student_last_name}",
                "course_name": c.course_name,
                "verification_code": c.verification_code,
                "issued_at": c.issued_at,
            }
            for c in paginated.items
        ]
    })


# ===================================
# EDIT CERTIFICATE
# ===================================
def update_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    data = request.get_json()

    cert.student_first_name = data.get("first_name", cert.student_first_name)
    cert.student_last_name = data.get("last_name", cert.student_last_name)
    cert.course_name = data.get("course_name", cert.course_name)
    cert.course_summary = data.get("course_summary", cert.course_summary)
    cert.year_of_study = data.get("year_of_study", cert.year_of_study)

    db.session.commit()

    return jsonify({"message": "Certificate updated successfully"})


# ===================================
# DELETE CERTIFICATE
# ===================================
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    db.session.delete(cert)
    db.session.commit()

    return jsonify({"message": "Certificate deleted successfully"})


def import_certificates_csv():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "CSV file is required"}), 400

    stream = StringIO(file.stream.read().decode("utf-8"))
    csv_reader = csv.DictReader(stream)

    created_count = 0
    errors = []

    for row in csv_reader:
        try:
            cert_num = generate_certificate_number(row["course_name"])
            qr_path = generate_certificate_qr(
                f"{row['first_name']} {row['last_name']}",
                row["course_name"],
                cert_num,
                row["issuance_date"]
            )

            cert = Certificate(
                student_first_name=row["first_name"],
                student_last_name=row["last_name"],
                course_name=row["course_name"],
                course_summary=row.get("course_summary"),
                year_of_study=row.get("year_of_study"),
                verification_code=cert_num,
                qr_code_url=qr_path,
                issued_at=row["issuance_date"]
            )

            db.session.add(cert)
            created_count += 1

        except Exception as e:
            errors.append(str(e))

    db.session.commit()

    return jsonify({
        "message": "CSV processed",
        "imported": created_count,
        "errors": errors
    })









# from ..models.certificate import Certificate
# from ..extensions import db
# from ..utils.code_generator import generate_unique_code
# from ..utils.pdf_generator import generate_certificate_pdf
# from ..utils.image_processor import pdf_to_image

# def create_certificate(data):
#     student_name = data.get("student_name")
#     course_name = data.get("course_name")

#     verification_code = generate_unique_code()

#     # Generate PDF
#     pdf_path = generate_certificate_pdf(student_name, course_name, verification_code)

#     # Generate image
#     image_path = pdf_to_image(pdf_path)

#     cert = Certificate(
#         student_name=student_name,
#         course_name=course_name,
#         verification_code=verification_code,
#         pdf_url=pdf_path,
#         image_url=image_path,
#     )

#     db.session.add(cert)
#     db.session.commit()

#     return {
#         "message": "Certificate created successfully",
#         "student_name": student_name,
#         "course_name": course_name,
#         "verification_code": verification_code,
#         "pdf_url": pdf_path,
#         "image_url": image_path,
#     }


