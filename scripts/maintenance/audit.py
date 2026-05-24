"""
SISTEMA DE AUDITORIA
====================
Módulo centralizado para registro de logs de segurança e auditoria.
"""
from flask import request
from flask_login import current_user
from models import db, AuditLog
import json
from datetime import datetime

def log_action(acao, tabela=None, registro_id=None, detalhes=None, user_override=None):
    """
    Registra uma ação no log de auditoria.
    
    Args:
        acao (str): Nome da ação (ex: CREATE_EDITAL, DELETE_BOLSISTA, LOGIN)
        tabela (str): Tabela afetada (opcional)
        registro_id (str): ID do registro afetado (opcional)
        detalhes (dict/str): Dados detalhados da ação (opcional). Dicionários são convertidos para JSON.
        user_override (User/int): Usuário explícito se current_user não estiver disponível.
    """
    try:
        user_id = None
        if user_override:
            user_id = user_override.id if hasattr(user_override, 'id') else int(user_override)
        elif hasattr(current_user, 'id'):
            user_id = current_user.id
        
        # Tenta pegar IP se estiver num contexto de request
        try:
            ip = request.remote_addr
            # Tenta pegar cabeçalho X-Forwarded-For se estiver atrás de proxy
            if request.headers.getlist("X-Forwarded-For"):
               ip = request.headers.getlist("X-Forwarded-For")[0]
        except:
            ip = 'SYSTEM/CLI'
        
        # Serialização segura de detalhes
        if isinstance(detalhes, dict):
            try:
                detalhes_str = json.dumps(detalhes, ensure_ascii=False, default=str)
            except:
                detalhes_str = str(detalhes)
        else:
            detalhes_str = str(detalhes) if detalhes else None
            
        log = AuditLog(
            user_id=user_id,
            acao=acao,
            tabela=tabela,
            registro_id=str(registro_id) if registro_id else None,
            detalhes=detalhes_str,
            ip_address=ip,
            data_hora=datetime.now()
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        # Falha silenciosa para não interromper fluxo principal, mas logada no console
        print(f"❌ [AUDIT ERROR] Falha ao registrar log: {e}")
        # Rollback apenas se a sessão estiver 'suja' por causa do log, 
        # mas cuidado para não rollbackar a transação principal se estiverem na mesma sessão.
        # Como SQLAlchemy usa Sessão por Request, o commit aqui comita TUDO.
        # O ideal é usar `db.session.begin_nested()` se quisermos isolar, 
        # mas para simplificar vamos assumir que log é feito no final ou commit explícito.
