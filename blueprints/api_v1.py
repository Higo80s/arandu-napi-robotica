from flask import Blueprint, request, jsonify
from flask_login import login_required
from extensions import db
from models import (
    RodadaSelecao, EditalRegra, EtapaCronograma, Candidatura
)
from utils import parse_flexible_date, sanitizar_cpf

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1_bp.route('/update-component', methods=['PATCH', 'POST', 'DELETE'])
@login_required
def update_component():
    """
    Unified Endpoint for Omni-Editor (v11)
    Supports: rodada, regra, etapa, candidato
    Methods: PATCH (Update), POST (Create), DELETE (Delete)
    """
    if request.method == 'DELETE':
        record_id = request.args.get('id')
        comp_type = request.args.get('component')
    else:
        data = request.json
        if not data:
            return jsonify(success=False, error="No data provided"), 400
        comp_type = data.get('component')
        record_id = data.get('id')
        payload = data.get('data', {})
        
    if not comp_type:
        return jsonify(success=False, error="Missing component type"), 400
        
    # Whitelist of allowed models for security
    allowed_models = {
        'rodada': (RodadaSelecao, ['nome', 'descricao', 'data_inicio', 'data_fim', 'ativa'], ['edital_id']),
        'regra': (EditalRegra, ['descricao', 'ordem'], ['edital_id']),
        'etapa': (EtapaCronograma, ['nome', 'data_inicio', 'data_limite', 'link_publicacao', 'ordem', 'concluida'], ['rodada_id']),
        'candidato': (Candidatura, ['nome', 'cpf', 'email', 'numero_sei', 'orientador', 'email_orientador', 'projeto_pesquisa', 'status', 'campus_id', 'programa_id', 'instituicao', 'cidade'], ['rodada_id'])
    }
    
    if comp_type not in allowed_models:
        return jsonify(success=False, error="Unsupported component type"), 400
        
    model_class, allowed_fields, parent_fields = allowed_models[comp_type]
    
    try:
        if request.method == 'POST':
            # [CREATE]
            record = model_class()
            # Set parent links (edital_id, rodada_id)
            for p_field in parent_fields:
                if p_field in payload:
                    setattr(record, p_field, payload[p_field])
            if comp_type == 'candidato':
                rodada_id = payload.get('rodada_id')
                if not rodada_id or not RodadaSelecao.query.get(rodada_id):
                    return jsonify(success=False, error="Rodada inválida"), 400
                max_ordem = db.session.query(db.func.max(Candidatura.ordem)).filter_by(rodada_id=rodada_id).scalar()
                record.ordem = (max_ordem if max_ordem is not None else -1) + 1
            db.session.add(record)
        else:
            # [UPDATE or DELETE]
            if not record_id:
                return jsonify(success=False, error="Missing id for update/delete"), 400
            record = model_class.query.get(record_id)
            if not record:
                return jsonify(success=False, error="Record not found"), 404

        if request.method == 'DELETE':
            # [DELETE]
            db.session.delete(record)
            db.session.commit()
            return jsonify(success=True)

        # [UPDATE or CREATE Fields]
        for field, value in payload.items():
            if field in allowed_fields:
                if comp_type == 'candidato' and field == 'cpf':
                    value = sanitizar_cpf(value) if value else value
                    if value:
                        duplicate = Candidatura.query.filter(
                            Candidatura.rodada_id == record.rodada_id,
                            Candidatura.cpf == value,
                            Candidatura.id != record.id,
                        ).first()
                        if duplicate:
                            return jsonify(success=False, error="Já existe candidatura com este CPF nesta rodada"), 400
                if comp_type == 'candidato' and field == 'status':
                    allowed_statuses = {'INSCRITO', 'SELECIONADO', 'EXCEDENTE', 'REJEITADO'}
                    if value not in allowed_statuses:
                        return jsonify(success=False, error="Status de candidatura inválido"), 400
                is_date_field = 'data' in field or 'fim' in field or 'inicio' in field or 'limite' in field
                if is_date_field and value and isinstance(value, str):
                    try:
                        value = parse_flexible_date(value)
                    except: pass 
                setattr(record, field, value)
        
        db.session.commit()
        try:
            from audit import log_action
            action_name = f"{request.method}_{comp_type.upper()}"
            log_action(action_name, tabela=model_class.__tablename__, registro_id=record.id, detalhes=f'Omni-Editor {request.method}: {list(payload.keys()) if payload else ""}')
        except Exception as log_err:
            print(f" [WARNING] Falha ao registrar log de auditoria: {log_err}")
            
        return jsonify(success=True, id=record.id)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500
