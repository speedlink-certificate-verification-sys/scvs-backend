# In app/__init__.py or app/cli.py
import click
from flask.cli import with_appcontext
import json
from datetime import datetime
from .extensions import db
from .models.student import Student
from .models.certificate import Certificate

@click.command('db-backup')
@with_appcontext
def backup_command():
    """Backup database to JSON file."""
    backup_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'students': [],
        'certificates': []
    }
    
    # Backup students
    for student in Student.query.all():
        backup_data['students'].append({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'course_name': student.course_name,
            'year_of_study': student.year_of_study
        })
    
    # Backup certificates
    for cert in Certificate.query.all():
        backup_data['certificates'].append({
            'id': cert.id,
            'verification_code': cert.verification_code,
            'student_name': f"{cert.student_first_name} {cert.student_last_name}",
            'course_name': cert.course_name
        })
    
    with open('database_backup.json', 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2)
    
    click.echo(f"✅ Backup created: database_backup.json")

# Register the command
def init_cli(app):
    app.cli.add_command(backup_command)