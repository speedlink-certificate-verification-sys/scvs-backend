from flask import request, jsonify
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.certificate import Certificate
from ..models.student import Student
from ..utils.certificate_number import generate_certificate_number
from ..utils.qr_generator import generate_certificate_qr
import csv
from io import StringIO
import pandas as pd
from io import BytesIO, StringIO


# # ===================================
# # CREATE CERTIFICATE
# # ===================================
# def create_certificate():
#     data = request.get_json()

#     first_name = data.get("first_name")
#     last_name = data.get("last_name")
#     course_name = data.get("course_name")
#     course_summary = data.get("course_summary")
#     year_of_study = data.get("year_of_study")
#     issuance_date = data.get("issuance_date")  # frontend controls this

#     # Generate cert number (course code is optional now)
#     certificate_number = generate_certificate_number(course_name)

#     # Generate QR
#     qr_path = generate_certificate_qr(
#         f"{first_name} {last_name}",
#         course_name,
#         certificate_number,
#         issuance_date
#     )

#     cert = Certificate(
#         student_first_name=first_name,
#         student_last_name=last_name,
#         course_name=course_name,
#         course_summary=course_summary,
#         year_of_study=year_of_study,
#         verification_code=certificate_number,
#         qr_code_url=qr_path,
#         issued_at=issuance_date,
#     )

#     db.session.add(cert)
#     db.session.commit()

#     return jsonify({
#         "message": "Certificate created successfully",
#         "certificate_number": certificate_number,
#     }), 201


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
    issuance_date = data.get("issuance_date")
    
    # NEW: Find or create student
    student = Student.query.filter_by(
        first_name=first_name,
        last_name=last_name,
        email=data.get("email")  # You might want to add email to your form
    ).first()
    
    # If student doesn't exist, create one
    if not student:
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=data.get("email", f"{first_name}.{last_name}@example.com"),  # Default email
            phone_number=data.get("phone_number"),
            course_name=course_name,
            year_of_study=year_of_study
        )
        db.session.add(student)
        db.session.flush()  # This gets the student ID without committing

    # Generate cert number
    certificate_number = generate_certificate_number(course_name)

    # Generate QR
    qr_path = generate_certificate_qr(
        f"{first_name} {last_name}",
        course_name,
        certificate_number,
        issuance_date
    )

    cert = Certificate(
        student_id=student.id,  # NEW: Add student_id
        student_first_name=first_name,  # Keep for backward compatibility
        student_last_name=last_name,    # Keep for backward compatibility
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
        "student_id": student.id  # NEW: Return student ID
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
                "student_id": c.student_id,  # NEW: Include student_id
                "student_name": f"{c.student_first_name} {c.student_last_name}",
                "course_name": c.course_name,
                "verification_code": c.verification_code,
                "issued_at": c.issued_at,
                # Optional: Include student email if needed
                "student_email": c.student.email if c.student else None
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
        return jsonify({"error": "File is required"}), 400

    filename = file.filename.lower()
    created_count = 0
    errors = []

    try:
        # Handle CSV files
        if filename.endswith('.csv'):
            # Try different encodings for CSV files
            file_content = file.read()
            
            # Try common encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            decoded_content = None
            
            for encoding in encodings:
                try:
                    decoded_content = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded_content is None:
                return jsonify({"error": "Unable to decode CSV file. Please ensure it's a valid CSV with standard encoding."}), 400
            
            stream = StringIO(decoded_content)
            csv_reader = csv.DictReader(stream)
            rows = list(csv_reader)

        # Handle Excel files
        elif filename.endswith(('.xlsx', '.xls')):
            # Read Excel file
            df = pd.read_excel(file)
            # Convert to list of dictionaries
            rows = df.to_dict('records')
        
        else:
            return jsonify({"error": "Unsupported file format. Please upload CSV or Excel file."}), 400

        # Process rows
        for row in rows:
            try:
                # Handle different column name formats
                first_name = row.get("first_name") or row.get("First Name") or row.get("First_Name")
                last_name = row.get("last_name") or row.get("Last Name") or row.get("Last_Name")
                course_name = row.get("course_name") or row.get("Course Name") or row.get("Course_Name")
                course_summary = row.get("course_summary") or row.get("Course Summary") or row.get("Course_Summary")
                year_of_study = row.get("year_of_study") or row.get("Year of Study") or row.get("Year_of_Study")
                issuance_date = row.get("issuance_date") or row.get("Issuance Date") or row.get("Issuance_Date")

                # Validate required fields
                if not all([first_name, last_name, course_name, issuance_date]):
                    errors.append(f"Missing required fields for row: {row}")
                    continue

                cert_num = generate_certificate_number(course_name)
                qr_path = generate_certificate_qr(
                    f"{first_name} {last_name}",
                    course_name,
                    cert_num,
                    issuance_date
                )

                cert = Certificate(
                    student_first_name=first_name,
                    student_last_name=last_name,
                    course_name=course_name,
                    course_summary=course_summary,
                    year_of_study=year_of_study,
                    verification_code=cert_num,
                    qr_code_url=qr_path,
                    issued_at=issuance_date
                )

                db.session.add(cert)
                created_count += 1

            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")

        db.session.commit()

        return jsonify({
            "message": "File processed successfully",
            "imported": created_count,
            "errors": errors,
            "total_rows": len(rows)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to process file: {str(e)}"
        }), 500

# def import_certificates_csv():
#     file = request.files.get("file")

#     if not file:
#         return jsonify({"error": "CSV file is required"}), 400

#     stream = StringIO(file.stream.read().decode("utf-8"))
#     csv_reader = csv.DictReader(stream)

#     created_count = 0
#     errors = []

#     for row in csv_reader:
#         try:
#             cert_num = generate_certificate_number(row["course_name"])
#             qr_path = generate_certificate_qr(
#                 f"{row['first_name']} {row['last_name']}",
#                 row["course_name"],
#                 cert_num,
#                 row["issuance_date"]
#             )

#             cert = Certificate(
#                 student_first_name=row["first_name"],
#                 student_last_name=row["last_name"],
#                 course_name=row["course_name"],
#                 course_summary=row.get("course_summary"),
#                 year_of_study=row.get("year_of_study"),
#                 verification_code=cert_num,
#                 qr_code_url=qr_path,
#                 issued_at=row["issuance_date"]
#             )

#             db.session.add(cert)
#             created_count += 1

#         except Exception as e:
#             errors.append(str(e))

#     db.session.commit()

#     return jsonify({
#         "message": "CSV processed",
#         "imported": created_count,
#         "errors": errors
#     })



