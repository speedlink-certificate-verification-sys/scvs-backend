from ..models.user import User

def generate_staff_id(role='admin', year_of_employment=None):
    """
    Generates a unique staff ID based on company, year, role.
    Format: SHSL/<year>/<dept>/<increment>
    """
    company_code = "SHSL"
    year_code = year_of_employment[-2:] if year_of_employment else "00"
    dept_code = role[:2].upper() if role else "AD"

    # Count existing staff in this department/year
    existing_count = User.query.filter(
        User.role==role,
        User.year_of_employment==year_of_employment
    ).count()

    increment = str(existing_count + 1).zfill(4)

    return f"{company_code}/{year_code}/{dept_code}/{increment}"
