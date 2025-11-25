from ..models.user import User
from ..extensions import db
from flask import jsonify, request
from ..utils.staff_id_generator import generate_staff_id

# -------------------------
# LIST ADMINS (Paginated)
# -------------------------
def list_admins():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = User.query.filter_by(role='admin').order_by(User.created_at.desc())
    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    admins = [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "phone_number": u.phone_number,
            "responsibility": u.responsibility,
            "year_of_employment": u.year_of_employment,
            "staff_id": u.staff_id,
            "created_at": u.created_at
        } for u in paginated.items
    ]

    return jsonify({
        "total": paginated.total,
        "page": page,
        "limit": limit,
        "admins": admins
    })


# -------------------------
# UPDATE ADMIN
# -------------------------
def update_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return {"message": "Admin not found"}, 404

    data = request.json
    admin.first_name = data.get('first_name', admin.first_name)
    admin.last_name = data.get('last_name', admin.last_name)
    admin.email = data.get('email', admin.email)
    admin.phone_number = data.get('phone_number', admin.phone_number)
    admin.responsibility = data.get('responsibility', admin.responsibility)
    admin.year_of_employment = data.get('year_of_employment', admin.year_of_employment)

    # regenerate staff_id if year changed
    if 'year_of_employment' in data:
        admin.staff_id = generate_staff_id(role='admin', year_of_employment=admin.year_of_employment)

    db.session.commit()

    return {
        "message": "Admin updated successfully",
        "admin": {
            "id": admin.id,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "email": admin.email,
            "phone_number": admin.phone_number,
            "responsibility": admin.responsibility,
            "year_of_employment": admin.year_of_employment,
            "staff_id": admin.staff_id,
            "created_at": admin.created_at
        }
    }


# -------------------------
# DELETE ADMIN
# -------------------------
def delete_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return {"message": "Admin not found"}, 404

    db.session.delete(admin)
    db.session.commit()

    return {"message": "Admin deleted successfully"}
