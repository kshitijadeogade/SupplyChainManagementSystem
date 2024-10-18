import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'        # Change if you used a different MySQL user
    MYSQL_PASSWORD = 'Test@123'  # Replace with your MySQL user's password
    MYSQL_DB = 'scm_db'
