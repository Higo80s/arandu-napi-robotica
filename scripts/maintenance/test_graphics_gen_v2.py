from app import app
from reports import gerar_relatorio_graficos
from datetime import datetime

with app.app_context():
    try:
        current_month = datetime.now().strftime("%Y-%m")
        print(f"Generating Graphics Report for {current_month}...")
        pdf_buffer = gerar_relatorio_graficos(current_month)
        
        file_path = "test_graficos_v2.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_buffer.read())
            
        print(f"Success! PDF generated at {file_path}")
        import os
        print(f"File size: {os.path.getsize(file_path)} bytes")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
