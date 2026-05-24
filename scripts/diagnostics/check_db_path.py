import os
import sqlite3

db_path = os.path.join(os.getcwd(), 'instance', 'gestao_editais_new.db')
instance_dir = os.path.dirname(db_path)

print(f"DB Path: {db_path}")
print(f"Instance Dir: {instance_dir}")

if not os.path.exists(instance_dir):
    print("Instance dir DOES NOT EXIST")
    try:
        os.makedirs(instance_dir)
        print("Created instance dir")
    except Exception as e:
        print(f"Failed to create dir: {e}")
else:
    print("Instance dir exists")

if os.path.exists(db_path):
    print(f"DB file exists. Size: {os.path.getsize(db_path)} bytes")
else:
    print("DB file DOES NOT EXIST")

try:
    conn = sqlite3.connect(db_path)
    print("Successfully connected to DB")
    conn.close()
except Exception as e:
    print(f"Failed to connect to DB: {e}")
