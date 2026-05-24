import psycopg2
from datetime import datetime

def init_ui_state():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port='5432', 
            user='postgres', 
            password='admin123', 
            database='gestao_editais'
        )
        cur = conn.cursor()
        
        # Default UI النصوص
        ui_data = [
            # Splash Screen
            ('title', 'NAPI-Robótica: Gestão Estratégica', 'splash'),
            ('loading_text', 'Sincronizando DNA Arandu...', 'splash'),
            ('step1', 'Acessando PostgreSQL (G.E.)', 'splash'),
            ('step2', 'Mapeando Projeto PI 33/2025', 'splash'),
            ('step3', 'Carregando Cockpit Master', 'splash'),
            ('step4', 'Renascimento da Interface Neon', 'splash'),
            
            # Dashboard
            ('dashboard_welcome', 'Bem-vindo ao Cockpit NAPI', 'dashboard'),
            ('integrity_msg_ok', 'Sistema Íntegro (SPARK-OK)', 'dashboard')
        ]
        
        print("Initializing UIState records...")
        for key, text, context in ui_data:
            cur.execute("""
                INSERT INTO ui_state (element_key, current_text, page_context, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (element_key) DO UPDATE SET current_text = EXCLUDED.current_text
            """, (key, text, context, datetime.now()))
        
        conn.commit()
        print("UIState Initialization Successful!")
        conn.close()
    except Exception as e:
        print(f"Error initializing UIState: {e}")

if __name__ == "__main__":
    init_ui_state()
