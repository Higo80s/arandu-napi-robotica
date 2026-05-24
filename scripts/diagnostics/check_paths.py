import os
import sys
from app_flask import app
import db

print("--- PATH DIAGNOSTIC ---")
print(f"CWD: {os.getcwd()}")
print(f"Flask URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Inspect db.py path logic
print(f"DB Module Path: {db.DB_PATH}")

# Check if they exist
flask_db = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
print(f"Flask DB Exists? {os.path.exists(flask_db)}")
print(f"DB Module DB Exists? {os.path.exists(db.DB_PATH)}")

# Check file sizes/timestamps to see if they are the same file
if flask_db and os.path.exists(flask_db):
    print(f"Flask DB Size: {os.path.getsize(flask_db)}")
else:
    print(f"Flask DB Missing: {flask_db}")

if hasattr(db, 'DB_PATH') and db.DB_PATH and os.path.exists(db.DB_PATH):
    print(f"DB Module DB Size: {os.path.getsize(db.DB_PATH)}")
else:
    print(f"DB Module DB Missing or Undefined: {getattr(db, 'DB_PATH', 'Not Found')}")

print("--- END DIAGNOSTIC ---")
