from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import AnotacaoSistema
from core.datetime_utils import utc_now, format_datetime_br

anotacoes_bp = Blueprint('anotacoes', __name__, url_prefix='/anotacoes')


def _pode_editar(anotacao):
    return (
        current_user.role in ['admin', 'master', 'gestor']
        or anotacao.user_id == current_user.id
    )


@anotacoes_bp.route('/')
@login_required
def index():
    filtro = request.args.get('filtro', 'pendentes')
    query = AnotacaoSistema.query
    if filtro == 'pendentes':
        query = query.filter(AnotacaoSistema.concluida.is_(False))
    elif filtro == 'concluidas':
        query = query.filter(AnotacaoSistema.concluida.is_(True))

    tarefas = query.order_by(
        AnotacaoSistema.concluida.asc(),
        AnotacaoSistema.criado_em.desc(),
    ).all()

    total_pendentes = AnotacaoSistema.query.filter_by(concluida=False).count()
    total_concluidas = AnotacaoSistema.query.filter_by(concluida=True).count()

    return render_template(
        'anotacoes/index.html',
        tarefas=tarefas,
        filtro=filtro,
        total_pendentes=total_pendentes,
        total_concluidas=total_concluidas,
    )


@anotacoes_bp.route('/api/novo', methods=['POST'])
@login_required
def api_novo():
    texto = request.form.get('texto')
    if not texto or not texto.strip():
        return jsonify({'success': False, 'message': 'Descreva a tarefa.'}), 400

    tarefa = AnotacaoSistema(
        user_id=current_user.id,
        texto=texto.strip(),
        concluida=False,
    )
    db.session.add(tarefa)
    db.session.commit()

    return jsonify({
        'success': True,
        'tarefa': {
            'id': tarefa.id,
            'texto': tarefa.texto,
            'concluida': tarefa.concluida,
            'criado_em': format_datetime_br(tarefa.criado_em),
            'autor': current_user.nome if current_user else 'Sistema',
        },
    })


@anotacoes_bp.route('/api/<int:id>/editar', methods=['POST'])
@login_required
def api_editar(id):
    tarefa = AnotacaoSistema.query.get_or_404(id)
    if not _pode_editar(tarefa):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    texto = request.form.get('texto')
    if not texto or not texto.strip():
        return jsonify({'success': False, 'message': 'O texto não pode ser vazio.'}), 400

    tarefa.texto = texto.strip()
    db.session.commit()

    return jsonify({
        'success': True,
        'texto': tarefa.texto,
        'atualizado_em': format_datetime_br(tarefa.atualizado_em),
    })


@anotacoes_bp.route('/api/<int:id>/toggle', methods=['POST'])
@login_required
def api_toggle(id):
    tarefa = AnotacaoSistema.query.get_or_404(id)
    if not _pode_editar(tarefa):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    tarefa.concluida = not tarefa.concluida
    tarefa.concluida_em = utc_now() if tarefa.concluida else None
    db.session.commit()

    return jsonify({
        'success': True,
        'concluida': tarefa.concluida,
        'concluida_em': (
            format_datetime_br(tarefa.concluida_em) if tarefa.concluida_em else None
        ),
    })


@anotacoes_bp.route('/api/<int:id>/excluir', methods=['POST'])
@login_required
def api_excluir(id):
    tarefa = AnotacaoSistema.query.get_or_404(id)
    if not _pode_editar(tarefa):
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    db.session.delete(tarefa)
    db.session.commit()
    return jsonify({'success': True})
