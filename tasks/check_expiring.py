"""
Script de Verificação de Bolsas Vencendo (Task 3.1.3)
=====================================================
Executa varredura diária para identificar bolsas próximas do vencimento (30 dias)
e envia notificações por e-mail.

Uso: python tasks/check_expiring.py
"""
import sys
import os
from datetime import date, datetime, timedelta

# Adicionar raiz do projeto ao path para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Bolsista
from utils.email_sender import send_email
from flask import render_template

def check_and_notify():
    print("=" * 60)
    print(f"🚀 START: Verificação de Bolsas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    with app.app_context():
        today = date.today()
        
        # Filtro: Apenas ativos
        bolsistas = Bolsista.query.filter_by(ativo=True).all()
        
        count = 0
        notified = 0
        
        # Destinatário das notificações (Configurado no .env ou padrão)
        # Idealmente seria o e-mail do orientador ou coordenador específico
        target_email = os.getenv('NOTIFICATION_EMAIL', 'admin@gestaoeditais.com')
        base_url = os.getenv('BASE_URL', 'http://127.0.0.1:5000')

        print(f"ℹ️  Analisando {len(bolsistas)} bolsistas ativos...")
        
        for b in bolsistas:
            if not b.data_fim_bolsa: continue
            
            dias_restantes = (b.data_fim_bolsa - today).days
            
            # Critério: Exatamente 30, 15 ou 7 dias? Ou intervalo?
            # Para evitar spam diário, o ideal é notificar em marcos específicos.
            # Marcos: 60, 30, 15, 7 dias.
            marcos = [60, 30, 15, 7, 3, 1]
            
            if dias_restantes in marcos:
                print(f"⚠️  [ALERTA] {b.nome}: Vence em {dias_restantes} dias. Enviando e-mail...")
                
                try:
                    # Constrói Link Manualmente para evitar problemas de contexto
                    link = f"{base_url}/bolsistas/{b.id}/editar"
                    
                    html_body = render_template('emails/bolsa_vencendo.html',
                        nome_bolsista=b.nome,
                        cpf=b.cpf or 'N/I',
                        modalidade=b.modalidade.nivel if b.modalidade else 'N/I',
                        edital=b.edital.numero if b.edital else 'N/I',
                        data_fim=b.data_fim_bolsa.strftime('%d/%m/%Y'),
                        dias_restantes=dias_restantes,
                        link_sistema=link
                    )
                    
                    subject = f"⚠️ [Gestão Editais] Bolsa Vencendo: {b.nome} ({dias_restantes} dias)"
                    
                    # Enviar
                    send_email(subject, [target_email], html_body)
                    notified += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao processar {b.nome}: {e}")
            
        print("-" * 60)
        print(f"✅ FIM: {notified} notificações enviadas.")

if __name__ == "__main__":
    check_and_notify()
