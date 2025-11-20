# Here you can use libraries like reportlab or fpdf to generate PDFs
# and qrcode to embed QR codes with the verification URL

import qrcode
from fpdf import FPDF
import os

def generate_certificate_pdf(student_name, course_name, verification_code, output_dir='pdfs'):
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{verification_code}.pdf")

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, f"Certificate for {student_name}", ln=True, align='C')
    pdf.cell(200, 10, f"Course: {course_name}", ln=True, align='C')
    pdf.cell(200, 10, f"Verification Code: {verification_code}", ln=True, align='C')

    # QR code
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(f"https://speedlinkng.com/certificate/{verification_code}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(output_dir, f"{verification_code}_qr.png")
    img.save(qr_path)

    pdf.image(qr_path, x=80, y=60, w=50, h=50)
    pdf.output(pdf_path)

    return pdf_path
