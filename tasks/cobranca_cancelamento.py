# --- tasks/cobranca_cancelamento.py ---
import os
from datetime import date
from collections import defaultdict
from flask import render_template
from flask_mail import Message
from extensions import db, mail
from models import Bolsista, User, ProgramaAcademico

def enviar_notificacoes_cancelamento(app):
    """
    Varre o sistema em busca de cancelamentos pendentes (Regra M+1)
    e envia e-mails consolidados para os coordenadores de programa.
    """
    with app.app_context():
        hoje = date.today()
        # Marco Zero: 1º dia do mês atual
        marco_zero = hoje.replace(day=1)
        
        # 1. Busca todos os bolsistas com cancelamento pendente
        # (Vencidos antes deste mês e ativos)
        pendencias = Bolsista.query.filter(
            Bolsista.ativo == True,
            Bolsista.data_fim_bolsa < marco_zero
        ).all()
        
        if not pendencias:
            print("[TAREFA] Nenhuma pendência crítica encontrada para notificação.")
            return

        # 2. Agrupa pendências por coordenador de programa
        # Estrutura: {coordenador_email: [lista_de_bolsistas]}
        mapa_notificacoes = defaultdict(list)
        
        for b in pendencias:
            # Tenta encontrar o coordenador do programa
            # Nota: Isso assume que o User tem relação com ProgramaAcademico ou filtro similar
            # Aqui usaremos uma lógica simplificada: busca usuários com role 'coordenador_programa' 
            # que tenham acesso ao programa do bolsista.
            
            # TODO: Refinar busca de coordenador específico por programa
            # Por enquanto, pegamos todos os coordenadores (Placeholder para implementação final)
            coordenadores = User.query.filter_by(role='coordenador_programa').all()
            
            for coord in coordenadores:
                # Aqui entraria a regra de permissão (coord -> programa)
                # Se o coordenador tem acesso a este bolsista, adiciona à lista dele
                mapa_notificacoes[coord.email].append(b)

        # 3. Dispara os e-mails
        email_count = 0
        for destinatario, lista_bolsistas in mapa_notificacoes.items():
            try:
                msg = Message(
                    f"⚠️ [Arandú] Pendências de Cancelamento de Bolsas - {hoje.strftime('%m/%Y')}",
                    recipients=[destinatario]
                )
                
                # Renderiza o template de e-mail
                msg.html = render_template(
                    'emails/cobranca_cancelamento.html',
                    lista=lista_bolsistas,
                    data_ref=hoje,
                    total=len(lista_bolsistas)
                )
                
                mail.send(msg)
                email_count += 1
            except Exception as e:
                print(f"[ERRO] Falha ao enviar e-mail para {destinatario}: {str(e)}")

        print(f"[TAREFA] Notificação concluída. {email_count} e-mails enviados com {len(pendencias)} pendências.")

# --- Comando CLI para disparar manualmente ---
# Uso: flask send-alerts
def init_app_tasks(app):
    @app.cli.command("send-alerts")
    def send_alerts_command():
        """Envia alertas de cobrança de cancelamento (CLI)"""
        print("Iniciando varredura de pendências críticas...")
        enviar_notificacoes_cancelamento(app)
        print("Operação finalizada.")
