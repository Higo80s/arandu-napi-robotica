
import sys
import os

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def init_db():
    print("--- Docker DB Initialization ---")
    with app.app_context():
        # Check connection
        try:
            print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            print("SUCCESS: Tables created (if not existed).")
        except Exception as e:
            print(f"ERROR: Could not create tables. {e}")
            sys.exit(1)

if __name__ == "__main__":
    init_db()
