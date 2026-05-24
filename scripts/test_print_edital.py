import sys
import os
sys.path.append('.')
from app import app
from reports_bp import edital_report_print

with app.app_context():
    res = edital_report_print(1)
    if hasattr(res, 'data'):
        # It's a Flask Response
        print(res.get_data(as_text=True))
    else:
        # It's a string (rendered template)
        print(res)
