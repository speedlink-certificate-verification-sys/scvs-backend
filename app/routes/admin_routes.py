from flask import Blueprint, request, jsonify
from ..controllers.admin_controller import list_admins, update_admin, delete_admin
from flasgger import swag_from

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# -------------------------
# LIST ADMINS
# -------------------------
@admin_bp.get("/list")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "List admins",
    "description": "Returns a paginated list of admins.",
    "parameters": [
        {"in": "query", "name": "page", "type": "integer", "default": 1},
        {"in": "query", "name": "limit", "type": "integer", "default": 10}
    ],
    "responses": {
        "200": {"description": "List of admins returned successfully"}
    }
})
def list_admins_route():
    return list_admins()


# -------------------------
# UPDATE ADMIN
# -------------------------
@admin_bp.put("/<int:admin_id>/edit")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Update an admin",
    "description": "Updates admin details by admin ID.",
    "consumes": ["application/json"],
    "parameters": [
        {"in": "path", "name": "admin_id", "type": "integer", "required": True},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "responsibility": {"type": "string"},
                    "year_of_employment": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Admin updated successfully"},
        "404": {"description": "Admin not found"}
    }
})
def update_admin_route(admin_id):
    return update_admin(admin_id)


# -------------------------
# DELETE ADMIN
# -------------------------
@admin_bp.delete("/<int:admin_id>/delete")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Delete an admin",
    "description": "Deletes an admin by ID.",
    "parameters": [
        {"in": "path", "name": "admin_id", "type": "integer", "required": True}
    ],
    "responses": {
        "200": {"description": "Admin deleted successfully"},
        "404": {"description": "Admin not found"}
    }
})
def delete_admin_route(admin_id):
    return delete_admin(admin_id)
