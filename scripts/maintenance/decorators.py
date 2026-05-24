from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def require_role(roles):
    """
    Restringe acesso a usuários com roles específicas.
    Pode receber uma string única ou uma lista de roles.
    
    Exemplos:
    @require_role('admin')
    @require_role(['admin', 'coordenador'])
    
    Nota: Admin tem acesso irrestrito por padrão se a lógica assim permitir,
    mas aqui vamos checar explicitamente.
    """
    if not isinstance(roles, list):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Admin Mestre: Se o usuário é admin ou master, acesso liberado (Superuser)
            if current_user.role in ['admin', 'master']:
                return f(*args, **kwargs)
            
            # Verificação normal
            if current_user.role not in roles:
                flash('🔒 Acesso negado. Funcionalidade restrita.', 'danger')
                return redirect(request.referrer or url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Atalho para @require_role('admin')"""
    return require_role('admin')(f)
