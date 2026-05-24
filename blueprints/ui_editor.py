from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, UIState, UIMementoHistory
from datetime import datetime
import json
import bleach

ui_editor_bp = Blueprint('ui_editor', __name__, url_prefix='/admin/ui')

@ui_editor_bp.route('/save', methods=['POST'])
@login_required
def save_ui_changes():
    """
    Salva as alterações da UI e gera um ponto de restauração (Memento).
    """
    if current_user.role not in ['admin', 'master']:
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    data = request.get_json()
    if not data or 'changes' not in data:
        return jsonify({'success': False, 'message': 'Dados inválidos'}), 400

    changes = data['changes'] # Expected { element_key: new_text }
    description = data.get('description', f"Alteração via Editor Visual em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    try:
        # 1. CRIAR O MEMENTO (Snapshot do estado ATUAL antes de salvar)
        current_state = UIState.query.all()
        snapshot_dict = {item.element_key: item.current_text for item in current_state}
        
        if snapshot_dict:
            memento = UIMementoHistory(
                user_id=current_user.id,
                description=description,
                ui_snapshot=snapshot_dict
            )
            db.session.add(memento)

        # 2. ATUALIZAR O ESTADO COM AS NOVAS MUDANÇAS
        for key, text in changes.items():
            # Sanitização (Segurança recomendada)
            clean_text = bleach.clean(text, tags=['b', 'i', 'u', 'em', 'strong', 'span', 'br'], attributes={'span': ['style']})
            
            ui_item = UIState.query.filter_by(element_key=key).first()
            if ui_item:
                ui_item.current_text = clean_text
            else:
                ui_item = UIState(element_key=key, current_text=clean_text, page_context='auto-detected')
                db.session.add(ui_item)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Alterações salvas e memento criado!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@ui_editor_bp.route('/history')
@login_required
def history():
    """
    Lista o histórico de pontos de restauração.
    """
    if current_user.role not in ['admin', 'master']:
        flash('Acesso negado', 'danger')
        return redirect(url_for('index'))
    
    mementos = UIMementoHistory.query.order_by(UIMementoHistory.timestamp.desc()).all()
    return render_template('admin/ui_history.html', mementos=mementos)

@ui_editor_bp.route('/restore/<int:memento_id>', methods=['POST'])
@login_required
def restore(memento_id):
    """
    Restaura a UI para um estado anterior.
    """
    if current_user.role not in ['admin', 'master']:
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    memento = UIMementoHistory.query.get_or_404(memento_id)
    
    try:
        # 1. Criar um memento do estado ATUAL antes de restaurar (Segurança extra)
        current_state = UIState.query.all()
        snapshot_dict = {item.element_key: item.current_text for item in current_state}
        
        backup_memento = UIMementoHistory(
            user_id=current_user.id,
            description=f"Backup automático antes de restaurar o snapshot #{memento_id}",
            ui_snapshot=snapshot_dict
        )
        db.session.add(backup_memento)

        # 2. Sobrescrever UIState com o snapshot do memento
        # Para ser "bulletproof", limpamos e re-inserimos ou atualizamos todos.
        # Decisão: Limpar e re-inserir garante que chaves deletadas no passado sumam.
        UIState.query.delete()
        
        for key, text in memento.ui_snapshot.items():
            new_item = UIState(element_key=key, current_text=text)
            db.session.add(new_item)
            
        db.session.commit()
        flash(f'Interface restaurada para o estado de {memento.timestamp.strftime("%d/%m/%Y %H:%M")}', 'success')
        return redirect(url_for('ui_editor.history'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao restaurar: {e}', 'danger')
        return redirect(url_for('ui_editor.history'))
