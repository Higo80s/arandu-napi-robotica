from flask import Flask
from models import db, User
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        print(f"Conectando em: {app.config['SQLALCHEMY_DATABASE_URI']}")
        users = User.query.all()
        print(f"Users found: {len(users)}")
        for u in users:
            print(f"User: {u.email} - Role: {getattr(u, 'role', 'UNDEFINED')}")
    except Exception as e:
        import traceback
        traceback.print_exc()
