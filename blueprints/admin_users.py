from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, ProgramaAcademico, Campus
from audit import log_action

admin_users_bp = Blueprint('admin_users', __name__, url_prefix='/admin/users')

@admin_users_bp.before_request
@login_required
def check_admin():
    if current_user.role not in ['admin', 'master']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Forbidden', 'message': 'Acesso não autorizado.'}), 403
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('index'))

@admin_users_bp.route('/')
def index():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)

@admin_users_bp.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        programa_id = request.form.get('programa_id') or None
        campus_id = request.form.get('campus_id') or None
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).order_by(ProgramaAcademico.nome_programa.asc()).all()
            campi = Campus.query.order_by(Campus.nome).all()
            return render_template('admin/users/form.html', programas=programas, campuses=campi)
            
        user = User(
            nome=nome, 
            email=email, 
            role=role, 
            must_change_password=True,
            programa_id=programa_id,
            campus_id=campus_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_action('USER_CREATE', tabela='usuarios', registro_id=user.id, detalhes=f'Created by {current_user.email}')
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin_users.index'))
        
    # GET: Carregar listas para dropdowns
    programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).order_by(ProgramaAcademico.nome_programa.asc()).all()
    campi = Campus.query.order_by(Campus.nome).all()
    return render_template('admin/users/form.html', programas=programas, campi=campi)

@admin_users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.nome = request.form.get('nome')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.programa_id = request.form.get('programa_id') or None
        user.campus_id = request.form.get('campus_id') or None
        # Checkbox returns 'on' or None
        user.ativo = True if request.form.get('ativo') else False
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
            user.must_change_password = True # Force change if admin resets it
            
        db.session.commit()
        log_action('USER_UPDATE', tabela='usuarios', registro_id=user.id)
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_users.index'))
        
    # GET: Carregar listas para dropdowns
    programas = ProgramaAcademico.query.options(db.joinedload(ProgramaAcademico.campus)).order_by(ProgramaAcademico.nome_programa.asc()).all()
    campi = Campus.query.order_by(Campus.nome).all()
    return render_template('admin/users/form.html', user=user, programas=programas, campuses=campi)
