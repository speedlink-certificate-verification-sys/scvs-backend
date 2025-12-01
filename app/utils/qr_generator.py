# utils/qr_generator.py
import qrcode
import json
import io
from datetime import datetime
from .google_drive import drive_service

def generate_certificate_qr(student_name, course_name, certificate_number, issued_at):
    """Generate QR code and upload to Google Drive"""
    
    # Format date
    if hasattr(issued_at, 'isoformat'):
        issued_at_str = issued_at.isoformat()
    elif isinstance(issued_at, str):
        issued_at_str = issued_at
    else:
        issued_at_str = datetime.now().date().isoformat()

    # Create QR data
    qr_data = {
        "student_name": student_name,
        "course_name": course_name,
        "certificate_number": certificate_number,
        "issued_at": issued_at_str,
        "verify_url": f"https://speedlinktraining.com/verify/{certificate_number}"
    }
    
    json_str = json.dumps(qr_data)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_str)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    # Generate filename
    filename = f"{certificate_number.replace('/', '_')}.png"
    
    try:
        # Upload to Google Drive
        drive_url = drive_service.upload_file(img_bytes, filename)
        return drive_url
    except Exception as e:
        # If not authenticated, raise an error
        raise Exception(f"Google Drive not authenticated. Please authenticate first: {str(e)}")









# import qrcode
# import json
# import os
# import io
# from datetime import datetime
# from .google_drive_simple import drive_service  # Use the simple version


# def generate_certificate_qr(student_name, course_name, certificate_number, issued_at):
#     """Generate QR code and upload to Google Drive"""
    
#     # Handle both date objects and strings for issued_at
#     if hasattr(issued_at, 'isoformat'):
#         issued_at_str = issued_at.isoformat()
#     elif isinstance(issued_at, str):
#         issued_at_str = issued_at
#     else:
#         issued_at_str = datetime.now().date().isoformat()

#     # Create QR code data
#     qr_data = {
#         "student_name": student_name,
#         "course_name": course_name,
#         "certificate_number": certificate_number,
#         "issued_at": issued_at_str,
#         "verify_url": f"https://speedlinktraining.com/verify/{certificate_number}"
#     }

#     json_str = json.dumps(qr_data)

#     # Generate QR code
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(json_str)
#     qr.make(fit=True)

#     # Create image
#     img = qr.make_image(fill_color="black", back_color="white")
    
#     # Save to bytes
#     img_bytes = io.BytesIO()
#     img.save(img_bytes, format='PNG')
#     img_bytes = img_bytes.getvalue()

#     # Generate filename
#     filename = f"{certificate_number.replace('/', '_')}.png"
    
#     # Upload to Google Drive
#     try:
#         drive_url = drive_service.upload_qr_code(img_bytes, filename)
#         return drive_url
#     except Exception as e:
#         print(f"Error uploading to Google Drive: {e}")
#         # Fallback: save locally (temporarily for Render)
#         temp_dir = '/tmp/qrcodes'
#         os.makedirs(temp_dir, exist_ok=True)
#         temp_path = os.path.join(temp_dir, filename)
#         with open(temp_path, 'wb') as f:
#             f.write(img_bytes)
#         return temp_path










# import qrcode
# import json
# import os
# from datetime import datetime


# def generate_certificate_qr(student_name, course_name, certificate_number, issued_at, folder="static/qrcodes"):
#     os.makedirs(folder, exist_ok=True)

#     # Handle both date objects and strings for issued_at
#     if hasattr(issued_at, 'isoformat'):
#         # It's a datetime/date object - use isoformat
#         issued_at_str = issued_at.isoformat()
#     elif isinstance(issued_at, str):
#         # It's already a string - use as is
#         issued_at_str = issued_at
#     else:
#         # Fallback: use current date
#         issued_at_str = datetime.now().date().isoformat()

#     qr_data = {
#         "student_name": student_name,
#         "course_name": course_name,
#         "certificate_number": certificate_number,
#         "issued_at": issued_at.isoformat(),
#         "verify_url": f"https://speedlinktraining.com/verify/{certificate_number}"
#     }

#     json_str = json.dumps(qr_data)

#     filename = f"{certificate_number.replace('/', '_')}.png"
#     filepath = os.path.join(folder, filename)

#     img = qrcode.make(json_str)
#     img.save(filepath)

#     return filepath

