"""
WSGI configuration for PythonAnywhere deployment
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/gestao_editais'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import app as application

# Initialize database if needed
with application.app_context():
    from models import db
    db.create_all()
