import psycopg2

def init_ui_data():
    try:
        conn = psycopg2.connect(
            host='localhost', 
            port='5432', 
            user='postgres', 
            password='admin123', 
            database='gestao_editais'
        )
        cur = conn.cursor()
        
        ui_data = [
            # Splash Screen
            ('splash', 'title', 'Arandu | NAPI-Robótica'),
            ('splash', 'loading_text', 'Sincronizando DNA...'),
            ('splash', 'step1', 'Acessando Banco de Dados PostgreSQL'),
            ('splash', 'step2', 'Verificando Integridade do PI 33/2025'),
            ('splash', 'step3', 'Carregando Dashboard Cockpit'),
            ('splash', 'step4', 'Autenticando Governança Master'),
            
            # Dashboard Master
            ('dashboard', 'welcome_title', 'Bem-vindo ao Cockpit NAPI'),
            ('dashboard', 'project_id', 'PI 33/2025 - Robótica Educacional'),
            ('dashboard', 'balance_label', 'Saldo em Convênio'),
            ('dashboard', 'scanner_label', 'Scanner de Integridade')
        ]
        
        print("Populating 'ui_state' with NAPI-Robótica branding...")
        for page, key, text in ui_data:
            cur.execute("""
                INSERT INTO ui_state (page_context, element_key, current_text)
                VALUES (%s, %s, %s)
                ON CONFLICT (element_key) DO UPDATE SET current_text = EXCLUDED.current_text
            """, (page, key, text))
        
        conn.commit()
        print("UI Initialization Successful!")
        conn.close()
    except Exception as e:
        print(f"Error during UI Initialization: {e}")

if __name__ == "__main__":
    init_ui_data()
