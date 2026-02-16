# SpeedLink Certificate Management System - Backend API

## 📋 Overview

A robust Flask-based REST API for managing student certificates with QR code generation, Google Drive integration, and bulk import capabilities.

This system powers the SpeedLink Certificate Management Platform.

---

## 🚀 Features

### 🎓 Certificate Management

- **Create Certificates** – Generate unique certificates with QR codes  
- **Automatic Verification Codes** – System-generated unique certificate numbers  
- **QR Code Generation** – Automatic QR code creation and storage on Google Drive  
- **Bulk Import** – Import multiple certificates via CSV/Excel files  
- **Update/Delete** – Full CRUD operations on certificates  
- **Sample Templates** – Download sample files for bulk imports  

---

### 👨‍🎓 Student Management

- **Student Records** – Maintain comprehensive student profiles  
- **Certificate Tracking** – Link students to their certificates  
- **Bulk Operations** – Import/export student data  
- **Unique Email Validation** – Prevent duplicate student records  

---

### ⚙️ Technical Features

- **Google Drive Integration** – Automatic QR code storage and management  
- **Database Optimization** – N+1 query prevention with SQLAlchemy joins  
- **File Import Support** – CSV and Excel file processing  
- **RESTful API** – Structured endpoints with proper HTTP methods  
- **API Documentation** – Swagger/OpenAPI integration via Flasgger  

---

## 🛠️ Technology Stack

| Component | Technology |
|------------|------------|
| Framework | Flask (Python 3.8+) |
| Database | PostgreSQL + SQLAlchemy ORM |
| Migrations | Flask-Migrate |
| File Processing | Pandas, CSV, OpenPyXL |
| QR Generation | qrcode |
| API Documentation | Flasgger (Swagger UI) |
| Cloud Storage | Google Drive API |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   ├── certificate.py
│   │   └── student.py
│   ├── controllers/
│   │   ├── certificate_controller.py
│   │   └── student_controller.py
│   ├── routes/
│   │   ├── certificate_routes.py
│   │   └── student_routes.py
│   └── utils/
│       ├── certificate_number.py
│       ├── qr_generator.py
│       └── google_drive_simple.py
├── migrations/
├── requirements.txt
└── run.py
```

---

## 🔧 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Google Drive API credentials
- Virtual environment (recommended)

---

### 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd backend
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/speedlink_db
SECRET_KEY=your-secret-key-here
GOOGLE_CREDENTIALS_PATH=path/to/google-credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-google-drive-folder-id
FLASK_ENV=development
DEBUG=True
```

---

## 🗄️ Database Setup

```bash
flask db upgrade
```

---

## ▶️ Run the Application

```bash
python run.py
```

API Base URL:

```
http://localhost:5000
```

Swagger Documentation:

```
http://localhost:5000/apidocs
```

---

# 📚 API Documentation

---

## 🎓 Certificate Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | `/certificate/create` | Create a new certificate |
| GET | `/certificate/certificates` | List all certificates |
| PUT | `/certificate/certificates/<code>` | Update certificate by verification code |
| DELETE | `/certificate/certificates/<code>` | Delete certificate |
| POST | `/certificate/certificates/import` | Bulk import certificates |
| GET | `/certificate/download-sample` | Download sample template |

---

## 👨‍🎓 Student Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/students/list` | List all students |
| POST | `/students/create` | Create a new student |
| PUT | `/students/<id>/edit` | Update student by ID |
| DELETE | `/students/<id>/delete` | Delete student by ID |
| POST | `/students/import` | Bulk import students |
| GET | `/students/download-sample` | Download sample template |

---

# 💡 Usage Examples

---

## Create a Certificate

```bash
curl -X POST http://localhost:5000/certificate/create \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "course_name": "Web Development",
    "course_summary": "Full stack development course",
    "year_of_study": "2024",
    "issuance_date": "2024-12-15",
    "email": "john.doe@example.com"
  }'
```

---

## Import Students via CSV

```bash
curl -X POST http://localhost:5000/students/import \
  -F "file=@/path/to/students.csv"
```

---

## Download Sample Template

```bash
curl -X GET "http://localhost:5000/students/download-sample?format=csv" \
  -o student_template.csv
```

---

# 🔄 Data Models

---

## Certificate Model

```python
id: Integer (Primary Key)
student_id: Integer (Foreign Key to Student)
student_first_name: String
student_last_name: String
course_name: String
course_summary: Text
year_of_study: String
verification_code: String (Unique)
qr_code_url: String
issued_at: Date
created_at: DateTime
```

---

## Student Model

```python
id: Integer (Primary Key)
first_name: String
last_name: String
email: String (Unique)
phone_number: String
course_name: String
year_of_study: String
program_start_date: Date
program_end_date: Date
photo_url: String
created_at: DateTime
certificates: Relationship to Certificate
```

---

# 🚦 Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error description here"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request / Validation error |
| 404 | Resource not found |
| 500 | Internal server error |

---

# 🔒 Environment Variables

| Variable | Description | Required |
|----------|------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| SECRET_KEY | Flask secret key | Yes |
| GOOGLE_CREDENTIALS_PATH | Path to Google service account JSON | Yes |
| GOOGLE_DRIVE_FOLDER_ID | Google Drive folder ID | Yes |
| FLASK_ENV | Development/production mode | No |
| DEBUG | Enable debug mode | No |

---

# 📦 Key Dependencies

- Flask  
- Flask-SQLAlchemy  
- Flask-Migrate  
- Flasgger  
- psycopg2-binary  
- pandas  
- openpyxl  
- qrcode  
- google-api-python-client  
- python-dotenv  

---

# 🤝 Contributing

1. Fork the repository  
2. Create a feature branch  

```bash
git checkout -b feature/amazing-feature
```

3. Commit changes  

```bash
git commit -m "Add amazing feature"
```

4. Push to branch  

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request  

---

# 📝 License

Specify your license here.

---

# 📧 Contact

Add your contact information here.

---

> **Note:**  
> Make sure to configure your Google Drive API credentials and database before running the application.  
> QR codes are automatically generated, uploaded to Google Drive, and the public URLs are stored in the database.
