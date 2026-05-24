import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

with app.app_context():
    # PostgreSQL specific query
    sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'editais';"
    rows = db.session.execute(text(sql)).fetchall()
    print("--- EDITAIS COLUMNS ---")
    for r in rows:
        print(f"{r.column_name} ({r.data_type})")
