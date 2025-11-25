import qrcode
import json
import os
from datetime import datetime


def generate_certificate_qr(student_name, course_name, certificate_number, issued_at, folder="static/qrcodes"):
    os.makedirs(folder, exist_ok=True)

    qr_data = {
        "student_name": student_name,
        "course_name": course_name,
        "certificate_number": certificate_number,
        "issued_at": issued_at.isoformat(),
        "verify_url": f"https://speedlinktraining.com/verify/{certificate_number}"
    }

    json_str = json.dumps(qr_data)

    filename = f"{certificate_number.replace('/', '_')}.png"
    filepath = os.path.join(folder, filename)

    img = qrcode.make(json_str)
    img.save(filepath)

    return filepath








# import qrcode
# import os
# from datetime import datetime

# def generate_qr_code(data, folder="static/qrcodes"):
#     os.makedirs(folder, exist_ok=True)

#     filename = f"{datetime.utcnow().timestamp()}_{data}.png"
#     filepath = os.path.join(folder, filename)

#     img = qrcode.make(data)
#     img.save(filepath)

#     return filepath






# import qrcode
# import os

# def generate_qr_code(data, output_dir='qrcodes'):
#     os.makedirs(output_dir, exist_ok=True)
#     path = os.path.join(output_dir, f"{data}.png")

#     qr = qrcode.QRCode(box_size=10, border=2)
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill="black", back_color="white")
#     img.save(path)
#     return path
