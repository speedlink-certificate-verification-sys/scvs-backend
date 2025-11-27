import os
from app import create_app, db
from sqlalchemy import text

# Set the database URL explicitly
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://admin:adminpassword@192.168.10.27:10010/scvs_db'

# Create the app instance
app = create_app()

with app.app_context():
    try:
        # Using text() for safer SQL execution
        with db.engine.begin() as connection:
            connection.execute(text("ALTER TABLE students ALTER COLUMN photo_url TYPE TEXT;"))
        
        print("✅ Column updated successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")