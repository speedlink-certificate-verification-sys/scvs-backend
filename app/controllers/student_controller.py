from datetime import datetime
from io import StringIO
from flask import Response, request, jsonify
from ..models.student import Student
from ..models.certificate import Certificate
from ..extensions import db
import csv
import os

# -------------------------
# LIST STUDENTS (Paginated)
# -------------------------
def list_students():
    # Remove pagination parameters
    query = Student.query.order_by(Student.created_at.desc())
    
    # Get all students
    all_students = query.all()

    students = []
    for s in all_students:
        # Get student_id from first certificate if exists
        student_id = None
        if s.certificates:
            # Take the verification code from the first certificate
            verification_code = s.certificates[0].verification_code
            # Remove "SHSL/" prefix if present
            if verification_code.startswith("SHSL/"):
                student_id = verification_code[5:]  # "25B/DM/0027"
            else:
                student_id = verification_code
        
        students.append({
            "id": s.id,
            "student_id": student_id,  # Add the extracted student_id
            "first_name": s.first_name,
            "last_name": s.last_name,
            "email": s.email,
            "phone_number": s.phone_number,
            "course_name": s.course_name,
            "year_of_study": s.year_of_study,
            "status": "Certified" if s.certificates else "Not Certified",
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else None,
            "certificate_count": len(s.certificates) if s.certificates else 0,
            "verification_code": s.certificates[0].verification_code if s.certificates else None  # Optional: include full code
        })

    return jsonify({
        "students": students,
        "count": len(students)
    })

# def list_students():
#     # Remove pagination parameters
#     query = Student.query.order_by(Student.created_at.desc())
    
#     # Get all students
#     all_students = query.all()

#     students = []
#     for s in all_students:
#         students.append({
#             "id": s.id,
#             "first_name": s.first_name,
#             "last_name": s.last_name,
#             "email": s.email,
#             "phone_number": s.phone_number,
#             "course_name": s.course_name,
#             "year_of_study": s.year_of_study,
#             "status": "Certified" if s.certificates else "Not Certified",
#             "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else None,
#             "certificate_count": len(s.certificates) if s.certificates else 0
#         })

#     return jsonify({
#         "students": students,
#         "count": len(students)
#     })


# -------------------------
# CREATE STUDENT
# -------------------------
def create_student():
    try:
        data = request.json
        
        # Check if student with email already exists
        existing_student = Student.query.filter_by(email=data.get("email")).first()
        if existing_student:
            return {
                "error": "Student with this email already exists",
                "student_id": existing_student.id,
                "existing_student": {
                    "first_name": existing_student.first_name,
                    "last_name": existing_student.last_name,
                    "email": existing_student.email
                }
            }, 400

        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "course_name"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return {
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        # Parse dates if provided
        program_start_date = None
        program_end_date = None
        
        if data.get("program_start_date"):
            try:
                program_start_date = datetime.strptime(data.get("program_start_date"), '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid program_start_date format. Use YYYY-MM-DD"}, 400
        
        if data.get("program_end_date"):
            try:
                program_end_date = datetime.strptime(data.get("program_end_date"), '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid program_end_date format. Use YYYY-MM-DD"}, 400

        student = Student(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone_number=data.get("phone_number"),
            course_name=data.get("course_name"),
            year_of_study=data.get("year_of_study"),
            program_start_date=program_start_date,
            program_end_date=program_end_date,
        )
        
        db.session.add(student)
        db.session.commit()

        return {
            "message": "Student created successfully", 
            "student_id": student.id,
            "student": {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "course_name": student.course_name
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {
            "error": f"Failed to create student: {str(e)}"
        }, 500
    
# def create_student():
#     data = request.json
#     student = Student(
#         first_name=data.get("first_name"),
#         last_name=data.get("last_name"),
#         email=data.get("email"),
#         phone_number=data.get("phone_number"),
#         course_name=data.get("course_name"),
#         year_of_study=data.get("year_of_study"),
#         program_start_date=data.get("program_start_date"),
#         program_end_date=data.get("program_end_date"),
#         # photo_url=data.get("photo_url")
#     )
#     db.session.add(student)
#     db.session.commit()

#     return {"message": "Student created successfully", "student_id": student.id}


# -------------------------
# UPDATE STUDENT
# -------------------------
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Student not found"}, 404

    data = request.json
    student.first_name = data.get("first_name", student.first_name)
    student.last_name = data.get("last_name", student.last_name)
    student.email = data.get("email", student.email)
    student.phone_number = data.get("phone_number", student.phone_number)
    student.course_name = data.get("course_name", student.course_name)
    student.year_of_study = data.get("year_of_study", student.year_of_study)
    student.program_start_date = data.get("program_start_date", student.program_start_date)
    student.program_end_date = data.get("program_end_date", student.program_end_date)
    student.photo_url = data.get("photo_url", student.photo_url)

    db.session.commit()
    return {"message": "Student updated successfully"}


# -------------------------
# DELETE STUDENT
# -------------------------
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Student not found"}, 404

    db.session.delete(student)
    db.session.commit()
    return {"message": "Student deleted successfully"}


# -------------------------
# IMPORT STUDENTS FROM CSV
# -------------------------
def import_students_csv():
    file = request.files.get("file")
    if not file:
        return {"message": "No CSV file provided"}, 400

    # Save uploaded CSV temporarily
    filepath = os.path.join("tmp", file.filename)
    os.makedirs("tmp", exist_ok=True)
    file.save(filepath)

    created_count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student = Student(
                first_name=row.get("first_name"),
                last_name=row.get("last_name"),
                email=row.get("email"),
                phone_number=row.get("phone_number"),
                course_name=row.get("course_name"),
                year_of_study=row.get("year_of_study"),
                program_start_date=row.get("program_start_date"),
                program_end_date=row.get("program_end_date"),
                photo_url=row.get("photo_url")
            )
            db.session.add(student)
            created_count += 1
        db.session.commit()

    os.remove(filepath)
    return {"message": f"{created_count} students imported successfully"}



# Add this to your student_controller.py file

# -------------------------
# DOWNLOAD SAMPLE STUDENT FILE
# -------------------------
def download_sample_student_file():
    """Generate and download a sample CSV/Excel template for student import"""
    
    file_format = request.args.get('format', 'csv').lower()
    
    # Sample data for student import - matching your CSV import structure
    sample_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+2348012345678",
            "course_name": "Web Development",
            "year_of_study": "2024",
            "program_start_date": "2024-01-15",
            "program_end_date": "2024-06-30",
            "photo_url": "https://example.com/photos/john_doe.jpg"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+2348123456789",
            "course_name": "Data Science",
            "year_of_study": "2024",
            "program_start_date": "2024-02-10",
            "program_end_date": "2024-07-25",
            "photo_url": "https://example.com/photos/jane_smith.jpg"
        },
        {
            "first_name": "Michael",
            "last_name": "Johnson",
            "email": "michael.johnson@example.com",
            "phone_number": "+2348234567890",
            "course_name": "UI/UX Design",
            "year_of_study": "2025",
            "program_start_date": "2025-01-05",
            "program_end_date": "2025-06-20",
            "photo_url": ""
        },
        {
            "first_name": "Sarah",
            "last_name": "Williams",
            "email": "sarah.williams@example.com",
            "phone_number": "+2348345678901",
            "course_name": "Cybersecurity",
            "year_of_study": "2024",
            "program_start_date": "2024-03-01",
            "program_end_date": "2024-08-15",
            "photo_url": "https://example.com/photos/sarah_w.jpg"
        }
    ]
    
    # Create filename with timestamp for uniqueness
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"student_import_template_{timestamp}.{file_format}"
    
    if file_format == 'csv':
        # Create CSV
        output = StringIO()
        if sample_data:
            # Get fieldnames from the first row
            fieldnames = sample_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        # Create response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        return response
        
    elif file_format in ['xlsx', 'excel']:
        try:
            # Create Excel file
            import pandas as pd
            from io import BytesIO
            
            df = pd.DataFrame(sample_data)
            output = BytesIO()
            
            # Create Excel file with pandas
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Students', index=False)
                
                # Add instructions sheet
                instructions_data = {
                    'Field': [
                        'first_name', 
                        'last_name', 
                        'email', 
                        'phone_number', 
                        'course_name', 
                        'year_of_study',
                        'program_start_date',
                        'program_end_date',
                        'photo_url'
                    ],
                    'Description': [
                        'Student\'s first name (required)',
                        'Student\'s last name (required)',
                        'Student\'s email address (required, must be unique)',
                        'Student\'s phone number (optional)',
                        'Course or program name (required)',
                        'Year of study (optional)',
                        'Program start date (YYYY-MM-DD format, optional)',
                        'Program end date (YYYY-MM-DD format, optional)',
                        'URL to student photo (optional)'
                    ],
                    'Example': [
                        'John',
                        'Doe',
                        'john.doe@example.com',
                        '+2348012345678',
                        'Web Development',
                        '2024',
                        '2024-01-15',
                        '2024-06-30',
                        'https://example.com/photo.jpg'
                    ]
                }
                instructions_df = pd.DataFrame(instructions_data)
                instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
                
                # Auto-adjust column widths for Students sheet
                worksheet = writer.sheets['Students']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Auto-adjust column widths for Instructions sheet
                worksheet_instructions = writer.sheets['Instructions']
                for column in worksheet_instructions.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 60)
                    worksheet_instructions.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            # Create response
            response = Response(
                output.read(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
            )
            return response
            
        except ImportError:
            # Fallback to CSV if pandas/openpyxl not available
            return jsonify({"error": "Excel export requires pandas and openpyxl. Please install them or use CSV format."}), 500
    
    else:
        return jsonify({"error": "Unsupported file format. Use 'csv' or 'xlsx'"}), 400
    