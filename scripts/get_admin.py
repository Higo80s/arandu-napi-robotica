import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import User

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(admin.email)
    else:
        print("No admin found")
