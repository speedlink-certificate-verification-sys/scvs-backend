from flask import request, jsonify
from ..models.student import Student
from ..models.certificate import Certificate
from ..extensions import db
import csv
import os

# -------------------------
# LIST STUDENTS (Paginated)
# -------------------------
def list_students():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    query = Student.query.order_by(Student.created_at.desc())
    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    students = []
    for s in paginated.items:
        students.append({
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "email": s.email,
            "phone_number": s.phone_number,
            "course_name": s.course_name,
            "year_of_study": s.year_of_study,
            "status": "Certified" if s.certificates else "Not Certified",
            "created_at": s.created_at
        })

    return jsonify({
        "total": paginated.total,
        "page": page,
        "limit": limit,
        "students": students
    })

# -------------------------
# CREATE STUDENT
# -------------------------
def create_student():
    data = request.json
    student = Student(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        phone_number=data.get("phone_number"),
        course_name=data.get("course_name"),
        year_of_study=data.get("year_of_study"),
        program_start_date=data.get("program_start_date"),
        program_end_date=data.get("program_end_date"),
        photo_url=data.get("photo_url")
    )
    db.session.add(student)
    db.session.commit()

    return {"message": "Student created successfully", "student_id": student.id}


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
