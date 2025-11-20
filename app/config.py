import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        # 'postgresql+psycopg2://username:password@localhost:5432/scvs_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
