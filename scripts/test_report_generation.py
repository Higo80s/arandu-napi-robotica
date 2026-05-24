import sys
import os

# Adjust path to find app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from reports_bp import audit_report_excel_route

with app.test_request_context():
    try:
        print("--- START REPORT GENERATION TEST ---")
        # executing the route function directly
        # It returns a Response object (send_file)
        response = audit_report_excel_route()
        print("--- REPORT GENERATION FINISHED ---")
        print("Success: Report generated without error.")
    except Exception as e:
        print(f"Error during report generation: {e}")
