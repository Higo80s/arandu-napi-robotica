import os
import sys
from app_flask import app
import db

print("--- PATH DIAGNOSTIC ---")
try:
    print(f"CWD: {os.getcwd()}")
    
    flask_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT_SET')
    print(f"Flask URI: {flask_uri}")
    
    flask_db_path = "UNKNOWN"
    if flask_uri.startswith('sqlite:///'):
        flask_db_path = flask_uri.replace('sqlite:///', '')
        
    print(f"Flask DB Path Resolved: {flask_db_path}")
    
    if os.path.exists(flask_db_path):
         print(f"Flask DB File Exists. Size: {os.path.getsize(flask_db_path)}")
    else:
         print(f"Flask DB File NOT FOUND at: {flask_db_path}")

    # Inspect DB module directly
    print("Inspecting db module...")
    db_path_mod = getattr(db, 'DB_PATH', None)
    print(f"db.DB_PATH: {db_path_mod}")
    
    if db_path_mod and os.path.exists(db_path_mod):
        print(f"Module DB File Exists. Size: {os.path.getsize(db_path_mod)}")
    elif db_path_mod:
        print(f"Module DB File NOT FOUND at: {db_path_mod}")
    else:
        print("db.DB_PATH is None or Empty")

except Exception as e:
    print(f"CRITICAL ERROR IN SCRIPT: {e}")

print("--- END DIAGNOSTIC ---")
