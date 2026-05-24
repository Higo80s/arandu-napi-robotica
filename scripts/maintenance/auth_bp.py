
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db # Import db from models to avoid circular import with app.py

from audit import log_action

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            log_action('LOGIN_FAIL', tabela='usuarios', detalhes={'email': email, 'reason': 'Invalid credentials'}, user_override=user)
            flash('Email ou senha incorretos. Verifique seus dados.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.ativo:
            log_action('LOGIN_BLOCK', tabela='usuarios', detalhes={'email': email, 'reason': 'User inactive'}, user_override=user)
            flash('Usuário inativo. Contate o administrador.', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        log_action('LOGIN', tabela='usuarios', registro_id=user.id, user_override=user)
        
        # Redireciona para a página que o usuário tentou acessar
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_action('LOGOUT', tabela='usuarios', registro_id=current_user.id)
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.must_change_password:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        
        if len(new_pwd) < 6:
            flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
            return render_template('auth/change_password.html')
            
        if new_pwd != confirm_pwd:
            flash('As senhas não conferem.', 'danger')
            return render_template('auth/change_password.html')
            
        current_user.set_password(new_pwd)
        current_user.must_change_password = False
        db.session.commit()
        
        log_action('PASSWORD_CHANGE_B', tabela='usuarios', registro_id=current_user.id, detalhes='First access password change')
        
        flash('Senha atualizada com sucesso! Você já pode usar o sistema.', 'success')
        return redirect(url_for('index'))
        
    return render_template('auth/change_password.html')

@auth_bp.before_app_request
def check_password_change():
    """Força mudança de senha se a flag estiver ativa."""
    if current_user.is_authenticated and current_user.must_change_password:
        # Lista de endpoints permitidos (whitelist)
        allowed_endpoints = ['auth.change_password', 'auth.logout', 'static']
        
        if request.endpoint not in allowed_endpoints:
            return redirect(url_for('auth.change_password'))
