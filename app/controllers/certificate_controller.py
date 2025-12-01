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
from datetime import datetime
import re
from ..utils.google_drive_simple import drive_service 


# Helper function to extract Google Drive file ID
def extract_file_id_from_url(url):
    """Extract file ID from Google Drive URL"""
    if not url:
        return None
    
    patterns = [
        r'id=([\w-]+)',  # For uc?export=view&id=...
        r'/d/([\w-]+)',   # For /d/file_id/view
        r'/file/d/([\w-]+)'  # For /file/d/file_id
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


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
    issuance_date_str = data.get("issuance_date")  # This comes as string from frontend
    
    # Convert issuance_date string to date object
    if issuance_date_str:
        try:
            # Handle different date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
            issuance_date = datetime.strptime(issuance_date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                issuance_date = datetime.strptime(issuance_date_str, '%d/%m/%Y').date()
            except ValueError:
                # If parsing fails, use current date
                issuance_date = datetime.now().date()
    else:
        # If no date provided, use current date
        issuance_date = datetime.now().date()

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
            email=data.get("email", f"{first_name}.{last_name}@Speedlinkng.com"),  # Default email
            phone_number=data.get("phone_number"),
            course_name=course_name,
            year_of_study=year_of_study
        )
        db.session.add(student)
        db.session.flush()  # This gets the student ID without committing

    # Generate cert number
    certificate_number = generate_certificate_number(course_name, issuance_date)

    # Generate QR - now passing date object instead of string
    full_name = first_name + " " + last_name
    qr_url = generate_certificate_qr(
        f"{first_name} {last_name}",
        course_name,
        certificate_number,
        issuance_date  # Now this is a date object, not a string
    )

    cert = Certificate(
        student_id=student.id,  # NEW: Add student_id
        student_first_name=first_name,  # Keep for backward compatibility
        student_last_name=last_name,    # Keep for backward compatibility
        course_name=course_name,
        course_summary=course_summary,
        year_of_study=year_of_study,
        verification_code=certificate_number,
        # qr_code_url=qr_path,
        qr_code_url=qr_url,

        issued_at=issuance_date,  # Use the date object here too
    )

    db.session.add(cert)
    db.session.commit()

    return jsonify({
        "message": "Certificate created successfully",
        "certificate_number": certificate_number,
        "student_id": student.id,  # NEW: Return student ID
        "qr_code_url": qr_url
    }), 201


# ===================================
# PAGINATED LIST (Optimized, no N+1)
# ===================================
def list_certificates():
    # Remove pagination
    query = Certificate.query.options(
        joinedload(Certificate.student)
    ).order_by(Certificate.created_at.desc())

    # Get all certificates
    all_certificates = query.all()

    return jsonify({
        "certificates": [
            {
                "id": c.id,
                "student_id": c.student_id,
                "student_name": f"{c.student_first_name} {c.student_last_name}",
                "course_name": c.course_name,
                "verification_code": c.verification_code,
                "issued_at": c.issued_at.strftime("%a, %d %b %Y") if c.issued_at else None,
                "qr_code_url": c.qr_code_url,
                "student_email": c.student.email if c.student else None,
                "year_of_study": c.year_of_study,
                "course_summary": c.course_summary
            }
            for c in all_certificates
        ],
        "count": len(all_certificates)
    })

# def list_certificates():
#     page = int(request.args.get("page", 1))
#     limit = int(request.args.get("limit", 10))

#     # query = Certificate.query.order_by(Certificate.created_at.desc())

#     query = Certificate.query.options(
#         joinedload(Certificate.student)
#     ).order_by(Certificate.created_at.desc())

#     paginated = query.paginate(page=page, per_page=limit, error_out=False)

#     return jsonify({
#         "total": paginated.total,
#         "page": paginated.page,
#         "pages": paginated.pages,
#         "items": [
#             {
#                 "id": c.id,
#                 "student_id": c.student_id,  # NEW: Include student_id
#                 "student_name": f"{c.student_first_name} {c.student_last_name}",
#                 "course_name": c.course_name,
#                 "verification_code": c.verification_code,
#                 "issued_at": c.issued_at.strftime("%a, %d %b %Y") if c.issued_at else None,
#                 "qr_code_url": c.qr_code_url,
#                 # Optional: Include student email if needed
#                 "student_email": c.student.email if c.student else None
#             }
#             for c in paginated.items
#         ]
#     })


# ===================================
# EDIT CERTIFICATE
# ===================================
def update_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    data = request.get_json()

    old_first_name = cert.student_first_name
    old_last_name = cert.student_last_name
    old_course_name = cert.course_name


    cert.student_first_name = data.get("first_name", cert.student_first_name)
    cert.student_last_name = data.get("last_name", cert.student_last_name)
    cert.course_name = data.get("course_name", cert.course_name)
    cert.course_summary = data.get("course_summary", cert.course_summary)
    cert.year_of_study = data.get("year_of_study", cert.year_of_study)

    # If name or course changed, regenerate QR code
    if (cert.student_first_name != old_first_name or 
        cert.student_last_name != old_last_name or 
        cert.course_name != old_course_name):
        
        # Delete old QR code from Google Drive
        if cert.qr_code_url and 'google.com' in cert.qr_code_url:
            drive_service.delete_file_by_url(cert.qr_code_url)
        
        # Generate new QR code
        new_qr_url = generate_certificate_qr(
            f"{cert.student_first_name} {cert.student_last_name}",
            cert.course_name,
            cert.verification_code,
            cert.issued_at
        )
        cert.qr_code_url = new_qr_url

    db.session.commit()

    return jsonify({"message": "Certificate updated successfully", "qr_code_url": cert.qr_code_url})


# ===================================
# DELETE CERTIFICATE
# ===================================
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)

    # Delete QR code from Google Drive
    if cert.qr_code_url and 'google.com' in cert.qr_code_url:
        drive_service.delete_file_by_url(cert.qr_code_url)

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
            file_content = file.read()
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
            decoded_content = None
            
            for encoding in encodings:
                try:
                    decoded_content = file_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded_content is None:
                return jsonify({"error": "Unable to decode CSV file. Try saving as UTF-8."}), 400
            
            stream = StringIO(decoded_content)
            
            # Try different delimiters
            sample = decoded_content[:1000]
            delimiter = ',' if ',' in sample else '\t' if '\t' in sample else ';'
            
            csv_reader = csv.DictReader(stream, delimiter=delimiter)
            rows = list(csv_reader)

        # Handle Excel files
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            rows = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        
        else:
            return jsonify({"error": "Unsupported file format."}), 400

        if not rows:
            return jsonify({"error": "No data found in file"}), 400

        # Auto-detect column mapping
        first_row = rows[0]
        available_columns = list(first_row.keys())
        
        print(f"Available columns: {available_columns}")
        print(f"First row: {first_row}")

        # Auto-detect name column
        name_column = None
        for col in available_columns:
            col_lower = col.lower().strip()
            if any(keyword in col_lower for keyword in ['name', 'student', 'full']):
                name_column = col
                break
        if not name_column and available_columns:
            name_column = available_columns[0]

        # Auto-detect course column
        course_column = None
        for col in available_columns:
            col_lower = col.lower().strip()
            if any(keyword in col_lower for keyword in ['department', 'course', 'program', 'dept']):
                course_column = col
                break
        if not course_column and len(available_columns) > 1:
            course_column = available_columns[1]

        # Auto-detect certificate column
        cert_column = None
        for col in available_columns:
            col_lower = col.lower().strip()
            if any(keyword in col_lower for keyword in ['certificate', 'cert', 'number', 'no', 'code']):
                cert_column = col
                break
        if not cert_column and len(available_columns) > 2:
            cert_column = available_columns[2]

        print(f"Detected columns - Name: {name_column}, Course: {course_column}, Cert: {cert_column}")

        # Process rows
        for index, row in enumerate(rows, 1):
            try:
                full_name = str(row.get(name_column, '')).strip() if name_column else ''
                course_name = str(row.get(course_column, '')).strip() if course_column else ''
                cert_num = str(row.get(cert_column, '')).strip() if cert_column else ''

                if not full_name:
                    errors.append(f"Row {index}: No name found in column '{name_column}'")
                    continue
                if not course_name:
                    errors.append(f"Row {index}: No course found in column '{course_column}'")
                    continue

                # Parse name
                name_parts = full_name.split()
                first_name = name_parts[0] if name_parts else "Unknown"
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Student"

                # Generate certificate number if not provided
                if not cert_num:
                    cert_num = generate_certificate_number(course_name)
                else:
                    # FIX: Check if certificate with this number already exists
                    existing_cert = Certificate.query.filter_by(verification_code=cert_num).first()
                    if existing_cert:
                        errors.append(f"Row {index}: Certificate number '{cert_num}' already exists for student '{existing_cert.student_first_name} {existing_cert.student_last_name}'. Skipping.")
                        continue

                # Generate QR
                qr_path = generate_certificate_qr(
                    full_name,
                    course_name,
                    cert_num,
                    datetime.now().date()
                )

                # Find or create student
                student = Student.query.filter_by(
                    first_name=first_name,
                    last_name=last_name,
                    course_name=course_name
                ).first()

                if not student:
                    # Create a unique email
                    base_email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@example.com"
                    email = base_email
                    counter = 1
                    
                    # Ensure unique email
                    while Student.query.filter_by(email=email).first():
                        email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{counter}@example.com"
                        counter += 1
                    
                    student = Student(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        course_name=course_name,
                        year_of_study="2025"
                    )
                    db.session.add(student)
                    db.session.flush()

                # FIX: Double-check certificate doesn't exist (in case of race condition)
                existing_cert_final = Certificate.query.filter_by(verification_code=cert_num).first()
                if existing_cert_final:
                    errors.append(f"Row {index}: Certificate number '{cert_num}' already exists. Skipping.")
                    continue

                # Create certificate
                cert = Certificate(
                    student_id=student.id,
                    student_first_name=first_name,
                    student_last_name=last_name,
                    course_name=course_name,
                    course_summary=f"Certificate for {course_name}",
                    year_of_study="2025",
                    verification_code=cert_num,
                    qr_code_url=qr_path,
                    issued_at=datetime.now().date()
                )

                db.session.add(cert)
                created_count += 1

            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")
                continue

        db.session.commit()

        return jsonify({
            "message": "File processed successfully",
            "imported": created_count,
            "errors": errors,
            "total_rows": len(rows),
            "detected_columns": {
                "name_column": name_column,
                "course_column": course_column, 
                "cert_column": cert_column
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500





# use this version for production 

    # 
# def import_certificates_csv():
#     file = request.files.get("file")

#     if not file:
#         return jsonify({"error": "File is required"}), 400

#     filename = file.filename.lower()
#     created_count = 0
#     errors = []

#     try:
#         # Handle CSV files
#         if filename.endswith('.csv'):
#             file_content = file.read()
#             encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
#             decoded_content = None
            
#             for encoding in encodings:
#                 try:
#                     decoded_content = file_content.decode(encoding)
#                     break
#                 except UnicodeDecodeError:
#                     continue
            
#             if decoded_content is None:
#                 return jsonify({"error": "Unable to decode CSV file. Try saving as UTF-8."}), 400
            
#             stream = StringIO(decoded_content)
            
#             # Try different delimiters
#             sample = decoded_content[:1000]
#             delimiter = ',' if ',' in sample else '\t' if '\t' in sample else ';'
            
#             csv_reader = csv.DictReader(stream, delimiter=delimiter)
#             rows = list(csv_reader)

#         # Handle Excel files
#         elif filename.endswith(('.xlsx', '.xls')):
#             df = pd.read_excel(file)
#             rows = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        
#         else:
#             return jsonify({"error": "Unsupported file format."}), 400

#         if not rows:
#             return jsonify({"error": "No data found in file"}), 400

#         # Auto-detect column mapping
#         first_row = rows[0]
#         available_columns = list(first_row.keys())
        
#         print(f"Available columns: {available_columns}")
#         print(f"First row: {first_row}")

#         # Auto-detect name column
#         name_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['name', 'student', 'full']):
#                 name_column = col
#                 break
#         if not name_column and available_columns:
#             name_column = available_columns[0]

#         # Auto-detect course column
#         course_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['department', 'course', 'program', 'dept']):
#                 course_column = col
#                 break
#         if not course_column and len(available_columns) > 1:
#             course_column = available_columns[1]

#         # Auto-detect certificate column
#         cert_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['certificate', 'cert', 'number', 'no', 'code']):
#                 cert_column = col
#                 break
#         if not cert_column and len(available_columns) > 2:
#             cert_column = available_columns[2]

#         print(f"Detected columns - Name: {name_column}, Course: {course_column}, Cert: {cert_column}")

#         # Process rows
#         for index, row in enumerate(rows, 1):
#             try:
#                 full_name = str(row.get(name_column, '')).strip() if name_column else ''
#                 course_name = str(row.get(course_column, '')).strip() if course_column else ''
#                 cert_num = str(row.get(cert_column, '')).strip() if cert_column else ''

#                 if not full_name:
#                     errors.append(f"Row {index}: No name found in column '{name_column}'")
#                     continue
#                 if not course_name:
#                     errors.append(f"Row {index}: No course found in column '{course_column}'")
#                     continue

#                 # Parse name
#                 name_parts = full_name.split()
#                 first_name = name_parts[0] if name_parts else "Unknown"
#                 last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Student"

#                 # Generate certificate number if not provided
#                 if not cert_num:
#                     cert_num = generate_certificate_number(course_name)

#                 # Generate QR
#                 qr_path = generate_certificate_qr(
#                     full_name,
#                     course_name,
#                     cert_num,
#                     datetime.now().date()
#                 )

#                 # FIX: Find or create student first
#                 student = Student.query.filter_by(
#                     first_name=first_name,
#                     last_name=last_name,
#                     course_name=course_name
#                 ).first()

#                 if not student:
#                     # Create a unique email
#                     base_email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@example.com"
#                     email = base_email
#                     counter = 1
                    
#                     # Ensure unique email
#                     while Student.query.filter_by(email=email).first():
#                         email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{counter}@example.com"
#                         counter += 1
                    
#                     student = Student(
#                         first_name=first_name,
#                         last_name=last_name,
#                         email=email,
#                         course_name=course_name,
#                         year_of_study="2025"
#                     )
#                     db.session.add(student)
#                     db.session.flush()  # Get the student ID without committing

#                 # Create certificate WITH student_id
#                 cert = Certificate(
#                     student_id=student.id,  # THIS IS THE CRITICAL FIX
#                     student_first_name=first_name,
#                     student_last_name=last_name,
#                     course_name=course_name,
#                     course_summary=f"Certificate for {course_name}",
#                     year_of_study="2025",
#                     verification_code=cert_num,
#                     qr_code_url=qr_path,
#                     issued_at=datetime.now().date()
#                 )

#                 db.session.add(cert)
#                 created_count += 1

#             except Exception as e:
#                 errors.append(f"Row {index}: {str(e)}")
#                 continue

#         db.session.commit()

#         return jsonify({
#             "message": "File processed successfully",
#             "imported": created_count,
#             "errors": errors,
#             "total_rows": len(rows),
#             "detected_columns": {
#                 "name_column": name_column,
#                 "course_column": course_column, 
#                 "cert_column": cert_column
#             }
#         })

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Failed to process file: {str(e)}"}), 500