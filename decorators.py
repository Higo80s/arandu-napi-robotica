from functools import wraps
from flask import abort, flash, redirect, url_for, request, jsonify
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
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Login required', 'redirect': url_for('auth.login')}), 401
                return redirect(url_for('auth.login'))
            
            # Admin Mestre: Se o usuário é admin ou master, acesso liberado (Superuser)
            if current_user.role in ['admin', 'master']:
                return f(*args, **kwargs)
            
            # Verificação normal
            if current_user.role not in roles:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Permissão negada', 'message': 'Seu nível de acesso não permite esta ação.'}), 403
                flash('🔒 Acesso negado. Funcionalidade restrita.', 'danger')
                return redirect(request.referrer or url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Atalho para @require_role('admin')"""
    return require_role('admin')(f)

def check_ownership(model_class):
    """
    [V14.1] Decorador para IDOR Hardening.
    Verifica se o usuário logado tem permissão de escopo para acessar o objeto pelo ID.
    
    Regras:
    - Admin/Gestor: Acesso total.
    - Diretor Campus: Acesso se campus_id bater.
    - Coordenador Programa: Acesso se programa_id bater.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            obj_id = kwargs.get('id')
            if not obj_id:
                return f(*args, **kwargs)
            
            # Superuser bypass
            if current_user.role in ['admin', 'master', 'gestor']:
                return f(*args, **kwargs)
            
            # Fetch object
            obj = model_class.query.get_or_404(obj_id)
            
            # Logic specific to Bolsista
            if model_class.__name__ == 'Bolsista':
                # Diretor de Campus: Valida via programa_link
                if current_user.role == 'diretor_campus':
                    campus_id = obj.programa_link.campus_id if obj.programa_link else None
                    if campus_id != current_user.campus_id:
                        log_action('SECURITY_VIOLATION_IDOR', tabela='bolsistas', registro_id=obj_id, detalhes=f"Usuário {current_user.email} tentou acessar bolsista de outro campus.")
                        flash("Acesso negado: Este bolsista pertence a outro campus.", "danger")
                        abort(403)
                
                # Coordenador de Programa: Valida programa_id direto
                elif current_user.role == 'coordenador_programa':
                    if obj.programa_id != current_user.programa_id:
                        log_action('SECURITY_VIOLATION_IDOR', tabela='bolsistas', registro_id=obj_id, detalhes=f"Usuário {current_user.email} tentou acessar bolsista de outro programa.")
                        flash("Acesso negado: Este bolsista pertence a outro programa.", "danger")
                        abort(403)
                        
            # Generic logic for other models can be added here
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
