from ..models.certificate import Certificate
from ..extensions import db
from datetime import datetime

def generate_certificate_number(course_code):
    """
    course_code examples:
    - DA
    - FO
    - GPD
    - CS/CEH
    """

    year = datetime.utcnow().year % 100   # 2025 -> 25
    batch_letter = "B"   # You can automate this later

    prefix = f"SHSL/{year}{batch_letter}/{course_code}"

    # Count how many certificates already exist for this course+year+batch
    existing_count = Certificate.query.filter(
        Certificate.verification_code.like(f"{prefix}/%")
    ).count()

    new_number = existing_count + 1

    formatted_number = str(new_number).zfill(4)  # 0001, 0002...

    return f"{prefix}/{formatted_number}"
