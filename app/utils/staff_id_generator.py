from ..models.user import User
from ..extensions import db

def generate_staff_id(role='admin', year_of_employment=None):
    """
    Generates a unique staff ID based on company, year, role.
    Format: SHSL/<year>/<dept>/<increment>
    """
    company_code = "SHSL"
    year_code = year_of_employment[-2:] if year_of_employment else "00"

    # Map role to department code (more specific)
    role_codes = {
        'admin': 'AD',
        'doctor': 'DR',
        'nurse': 'NR',
        'staff': 'ST',
        'intern': 'IN',
        'receptionist': 'RC',
        'accountant': 'AC'
    }
    dept_code = role_codes.get(role.lower(), 'AD')

    # Create the pattern to search for
    pattern = f"{company_code}/{year_code}/{dept_code}/%"
    
    # Find the highest existing number for this exact pattern
    last_user = User.query.filter(
        User.staff_id.like(pattern)
    ).order_by(User.staff_id.desc()).first()

    if last_user:
        try:
            # Extract the number part and increment
            last_number = int(last_user.staff_id.split('/')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # If parsing fails, start from 1
            new_number = 1
    else:
        # No users with this pattern yet, start from 0001
        new_number = 1

    # Format with leading zeros (4 digits)
    increment = str(new_number).zfill(4)
    
    staff_id = f"{company_code}/{year_code}/{dept_code}/{increment}"
    
    # Double-check this staff_id doesn't exist (safety net)
    if User.query.filter_by(staff_id=staff_id).first():
        # If by some chance it exists, try the next number
        new_number += 1
        increment = str(new_number).zfill(4)
        staff_id = f"{company_code}/{year_code}/{dept_code}/{increment}"

    return staff_id

    
    # dept_code = role[:2].upper() if role else "AD"

    # # Count existing staff in this department/year
    # existing_count = User.query.filter(
    #     User.role==role,
    #     User.year_of_employment==year_of_employment
    # ).count()

    # increment = str(existing_count + 1).zfill(4)

    # return f"{company_code}/{year_code}/{dept_code}/{increment}"
