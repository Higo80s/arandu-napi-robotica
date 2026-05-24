from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models import (
    Edital, Modalidade, Campus, ProgramaAcademico, Bolsista, 
    User, Residente, UIState, Acompanhamento, UIMementoHistory
)
import pandas as pd
from io import BytesIO
from decorators import admin_required
from sqlalchemy import inspect
from datetime import date

database_explorer_bp = Blueprint('database_explorer', __name__)

# Mapeamento de nomes de tabelas para as classes SQL Alchemy (para segurança e facilidade)
MODELS_MAP = {
    'bolsistas': Bolsista,
    'editais': Edital,
    'modalidades': Modalidade,
    'usuarios': User,
    'campi': Campus,
    'programas': ProgramaAcademico,
    'residentes': Residente,
    'ui_state': UIState,
    'acompanhamentos': Acompanhamento,
    'mementos': UIMementoHistory
}

SENSITIVE_FIELDS = ['password', 'senha', 'hash', 'token', 'secret', 'encryption_key', '_key']

@database_explorer_bp.route('/admin/database')
@login_required
@admin_required
def index():
    """Lista as tabelas disponíveis para exploração."""
    tables_info = []
    for name, model in MODELS_MAP.items():
        count = model.query.count()
        columns = [c.name for c in model.__table__.columns if not any(s in c.name.lower() for s in SENSITIVE_FIELDS)]
        tables_info.append({
            'name': name,
            'count': count,
            'description': model.__doc__ or f"Tabela de {name.capitalize()}",
            'columns': columns
        })
    
    return render_template('admin/database_explorer.html', tables=tables_info)

@database_explorer_bp.route('/admin/database/view/<table_name>')
@login_required
@admin_required
def view_table(table_name):
    """Exibe os dados brutos de uma tabela específica."""
    model = MODELS_MAP.get(table_name)
    if not model:
        flash("Tabela não encontrada ou acesso negado.", "danger")
        return redirect(url_for('database_explorer.index'))
    
    # Paginação simples
    page = request.args.get('page', 1, type=int)
    per_page = 100
    pagination = model.query.order_by(model.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Colunas (Filtrando sensíveis)
    all_columns = model.__table__.columns
    visible_columns = [c for c in all_columns if not any(s in c.name.lower() for s in SENSITIVE_FIELDS)]
    
    return render_template('admin/database_explorer_view.html', 
                           table_name=table_name,
                           pagination=pagination,
                           columns=visible_columns,
                           models_map=MODELS_MAP)

@database_explorer_bp.route('/admin/database/update/<table_name>/<int:record_id>', methods=['POST'])
@login_required
@admin_required
def update_record(table_name, record_id):
    """Atualização rápida de um campo (apenas campos permitidos)."""
    model = MODELS_MAP.get(table_name)
    if not model:
        return jsonify({'success': False, 'message': 'Tabela inválida'}), 400
    
    record = model.query.get_or_404(record_id)
    field = request.form.get('field')
    value = request.form.get('value')
    
    # Segurança: Verificar se o campo é editável (não é ID nem Foreign Key nem Sensível)
    column = model.__table__.columns.get(field)
    if not column or column.primary_key or len(column.foreign_keys) > 0 or any(s in field.lower() for s in SENSITIVE_FIELDS):
        return jsonify({'success': False, 'message': 'Este campo não é editável diretamente.'}), 403
    
    try:
        # Conversão de tipo básica baseada no SQLAlchemy
        from sqlalchemy import String, Integer, Float, Boolean, Date
        
        if isinstance(column.type, Integer):
            setattr(record, field, int(value) if value else None)
        elif isinstance(column.type, Float):
            setattr(record, field, float(value) if value else None)
        elif isinstance(column.type, Boolean):
            setattr(record, field, value.lower() in ('true', '1', 't', 'y'))
        else:
            setattr(record, field, value)
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Registro atualizado.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@database_explorer_bp.route('/admin/database/export/<table_name>')
@login_required
@admin_required
def export_table(table_name):
    """Exporta a tabela selecionada para Excel."""
    model = MODELS_MAP.get(table_name)
    if not model:
        flash("Tabela inválida.", "danger")
        return redirect(url_for('database_explorer.index'))
    
    # Busca todos os dados
    records = model.query.all()
    
    # Filtra colunas sensíveis
    visible_columns = [c.name for c in model.__table__.columns if not any(s in c.name.lower() for s in SENSITIVE_FIELDS)]
    
    data = []
    for r in records:
        row = {col: getattr(r, col) for col in visible_columns}
        data.append(row)
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=table_name.capitalize())
    
    output.seek(0)
    filename = f"Explorador_Dados_{table_name}_{date.today().strftime('%Y%m%d')}.xlsx"
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)
