from app import app
from reports import gerar_relatorio_pdf
from datetime import datetime

with app.app_context():
    try:
        current_month = datetime.now().strftime("%Y-%m")
        print(f"Generating PDF for {current_month}...")
        pdf_buffer = gerar_relatorio_pdf(current_month)
        
        # Save to file to verify size > 0
        file_path = "test_pagamento.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_buffer.read())
            
        print(f"Success! PDF generated at {file_path}")
        
        import os
        size = os.path.getsize(file_path)
        print(f"File size: {size} bytes")
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
