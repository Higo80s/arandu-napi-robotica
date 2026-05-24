import pandas as pd
from io import BytesIO
from datetime import date
from flask_mail import Message
from extensions import db, mail
from models import Bolsista, User, LogAutomacao

def enviar_relatorio_excel_semanal(app):
    """
    Gera o relatório de pendências M+1 em Excel e envia aos administradores,
    registrando cada passo no Monitor de Automação.
    """
    with app.app_context():
        # 1. Inicializa o Log de Observabilidade
        log = LogAutomacao(nome_tarefa="Relatório Semanal de Pendências (M+1)")
        hoje = date.today()
        marco_zero = hoje.replace(day=1)
        
        try:
            # 2. Coleta de Dados Otimizada
            # Filtramos bolsistas ativos cuja vigência encerrou antes do mês atual
            pendencias = Bolsista.query.filter(
                Bolsista.ativo == True,
                Bolsista.data_fim_bolsa < marco_zero
            ).all()

            if not pendencias:
                log.status = "SUCESSO"
                log.mensagem = "Execução concluída: Nenhuma pendência identificada no período."
                db.session.add(log)
                db.session.commit()
                return

            # 3. Construção do Relatório em Memória (Pandas)
            data = []
            for b in pendencias:
                # [FIX] programa_link instead of programa
                data.append({
                    'Campus': b.programa_link.campus.sigla_campus if b.programa_link and b.programa_link.campus else 'N/A',
                    'Programa': b.programa_link.sigla_programa if b.programa_link else 'N/A',
                    'Discente': b.nome,
                    'Edital': b.edital.numero if b.edital else 'Institucional',
                    'Vencimento': b.data_fim_bolsa.strftime('%d/%m/%Y'),
                    'Valor Mensal': b.modalidade.valor_mensal if b.modalidade else 0,
                    'Dias de Atraso': (hoje - b.data_fim_bolsa).days
                })
            
            df = pd.DataFrame(data)
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Pendencias M+1')
            excel_buffer.seek(0)

            # 4. Disparo do E-mail Institucional
            # [UPDATED] Use current_app context or passed app
            admins = [u.email for u in User.query.filter_by(role='admin', ativo=True).all()]
            if not admins:
                raise Exception("Nenhum administrador ativo encontrado para receber o relatório.")

            msg = Message(
                subject=f"📊 [ARANDÚ] Relatório de Governança - {hoje.strftime('%d/%m/%Y')}",
                recipients=admins,
                body=f"Prezados,\n\nSegue em anexo a lista de {len(pendencias)} bolsistas com cancelamento pendente.\n\nEste é um e-mail automático do sistema Arandú."
            )
            
            msg.attach(
                filename=f"relatorio_pendencias_{hoje.strftime('%Y%m%d')}.xlsx",
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                data=excel_buffer.read()
            )

            mail.send(msg)

            # 5. Registro de Sucesso
            log.status = "SUCESSO"
            log.registros_processados = len(pendencias)
            log.mensagem = f"E-mail enviado para {len(admins)} destinatários com {len(pendencias)} registros."

        except Exception as e:
            # 6. Captura de Falha Silenciosa (Blindagem)
            log.status = "ERRO"
            log.mensagem = f"Erro na automação: {str(e)}"
            log.registros_processados = 0

        finally:
            # 7. Persistência Incondicional do Log
            db.session.add(log)
            db.session.commit()
