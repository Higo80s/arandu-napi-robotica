
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, not_
import re
from decimal import Decimal

# Centralized Imports
from extensions import db
from models import (
    Bolsista, Edital, Modalidade, Campus, ProgramaAcademico, 
    Afastamento, DadosSociais, MobilidadeInternacional, AcordoInternacional,
    Candidatura, ComentarioBolsista
)
from audit import log_action
from utils import parse_flexible_date, format_date_br
from utils.permissions import apply_user_scope
from core.memento import BolsistaCaretaker
from blueprints.services.validation_strategies import ValidadorAcumuloContext, AcumuloBolsaAtivaStrategy, AcumuloProcessoSeletivoStrategy
from blueprints.services.sync_engine import SyncEngine, AcademicParser
from blueprints.services.reconciliation import get_conflitos, reconcile_merge, reconcile_keep_one, check_titulacao_conflito
from services.parser_strategy import StrictoSensuParser
from services.bolsista_service import BolsistaService
from services.funtef_onboarding_service import FuntefOnboardingService
from services.implantacao_bolsa_service import ImplantacaoBolsaService
from core.datetime_utils import utc_now
from decorators import require_role, admin_required, check_ownership

bolsistas_bp = Blueprint('bolsistas', __name__)

# --- HELPERS ---
def clean_currency(val):
    if not val: return Decimal('0')
    cleaned = re.sub(r'[^\d,]', '', val)
    return Decimal(cleaned.replace(',', '.'))

def _apply_funtef_fields(bolsista):
    """Campos do fluxo FUNTEF / Conveniar (form POST)."""
    bolsista.link_pasta_nuvem = request.form.get('link_pasta_nuvem', '').strip() or None
    bolsista.conveniar_cadastrado = 'conveniar_cadastrado' in request.form
    bolsista.funtef_contrato_pronto = 'funtef_contrato_pronto' in request.form


def _validate_funtef_fields(bolsista):
    """Valida etapas FUNTEF/Conveniar antes de persistir."""
    return FuntefOnboardingService.validate_stage_fields(
        bolsista,
        'conveniar_cadastrado' in request.form,
        request.form.get('link_pasta_nuvem', ''),
        'funtef_contrato_pronto' in request.form,
    )


def _flash_funtef_result(bolsista):
    ok, msg = FuntefOnboardingService.try_send_notification(bolsista, user_id=current_user.id)
    if ok and msg:
        flash(msg, 'success')
    elif msg:
        flash(msg, 'warning')


def _pagamentos_log(bolsista):
    """Linhas do log individual (mesmas regras da folha Nuvem)."""
    if not bolsista or not getattr(bolsista, 'id', None):
        return []
    from services.pagamento_bolsista_service import PagamentoBolsistaService
    return PagamentoBolsistaService.listar_pagamentos(bolsista)


def _registrar_comentario_desligamento(bolsista, user_id):
    """Registra desligamento no Histórico de comentários (aba auditoria)."""
    data_txt = format_date_br(bolsista.data_desligamento or bolsista.data_fim_bolsa) or '—'
    motivo = (bolsista.motivo_desligamento or 'Desligamento via sistema').strip()
    devolucao = 'Sim' if bolsista.devolucao_valores else 'Não'
    texto = (
        f'[DESLIGAMENTO] Bolsista desligado do projeto em {data_txt}.\n'
        f'Motivo: {motivo}\n'
        f'Devolução de valores: {devolucao}'
    )
    bolsista.comentarios_historico.append(
        ComentarioBolsista(texto=texto, user_id=user_id)
    )


CAMPUS_SIGLA_MAPPING = {
    'Apucarana': 'AP', 'Campo Mourão': 'CM', 'Cornélio Procópio': 'CP', 'Curitiba': 'CT',
    'Dois Vizinhos': 'DV', 'Francisco Beltrão': 'FB', 'Guarapuava': 'GP', 'Londrina': 'LD',
    'Medianeira': 'MD', 'Pato Branco': 'PB', 'Ponta Grossa': 'PG', 'Santa Helena': 'SH', 'Toledo': 'TD'
}

def get_sigla(campus_nome):
    if not campus_nome: return None
    return CAMPUS_SIGLA_MAPPING.get(campus_nome, campus_nome[:2].upper())

VALID_NAPI = ['UTFPR', 'UFPR', 'IFPR', 'UEL', 'UEM', 'UNIOESTE', 'UENP', 'IPB']

# --- ROUTES: BOLSISTAS ---

@bolsistas_bp.route('/bolsistas')
def index():
    edital_id = request.args.get('edital_id', type=int)
    search_q = request.args.get('q', '').strip()
    
    editais = Edital.query.all()
    
    query = Bolsista.query
    
    # [V22] Filtro de Escopo Hierárquico: Coordenador/Diretor veem apenas seus dados
    query = apply_user_scope(query, current_user, Bolsista)
    
    if edital_id:
        query = query.filter_by(edital_id=edital_id)
        
    if search_q:
        term = f"%{search_q}%"
        conditions = [
            Bolsista.nome.ilike(term),
            Bolsista.cpf.ilike(term),
            Bolsista.email.ilike(term),
            Bolsista.orientador.ilike(term),
            Bolsista.processo_sei.ilike(term),
            Bolsista.numero_formulario.ilike(term)
        ]
        
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.nome_programa.ilike(term)))
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.sigla_programa.ilike(term)))
        conditions.append(Bolsista.programa_link.has(ProgramaAcademico.codigo_programa.ilike(term)))
        
        query = query.filter(or_(*conditions))

    # Exclude Pos-Doc from main list
    query = query.join(Modalidade).filter(
        not_(or_(
            Modalidade.nivel.ilike('%PÓS%'),
            Modalidade.nivel.ilike('%Pós%'),
            Modalidade.nivel.ilike('%RESID%'), 
            Modalidade.nivel.ilike('%POS%')
        ))
    )
        
    bolsistas = query.all()

    # --- Sorting ---
    sort_by = request.args.get('sort', 'nome')
    order = request.args.get('order', 'asc')
    total_before_filter = len(bolsistas)
    
    if sort_by == 'status':
        from core.status_engine import BolsistaStatus
        # Agrupa por tipo de status (resumo); dentro do grupo, por nome.
        # Filtros legados (order=ativo|inativo|...) continuam disponíveis.
        status_group_order = {
            BolsistaStatus.ATIVO: 0,
            BolsistaStatus.ULTIMA_PARCELA: 1,
            BolsistaStatus.FINALIZANDO: 1,
            BolsistaStatus.SUSPENSO: 2,
            BolsistaStatus.AGUARDANDO_IMPLANTACAO: 3,
            BolsistaStatus.PENDENTE_GOVERNANCA: 3,
            BolsistaStatus.CANCELAMENTO_REQUERIDO: 4,
            BolsistaStatus.VENCIDO_CRITICO: 4,
            BolsistaStatus.INATIVO: 4,
        }
        status_filters = {
            'ativo': [BolsistaStatus.ATIVO],
            'inativo': [
                BolsistaStatus.INATIVO,
                BolsistaStatus.CANCELAMENTO_REQUERIDO,
                BolsistaStatus.VENCIDO_CRITICO,
            ],
            'finalizando': [BolsistaStatus.FINALIZANDO, BolsistaStatus.ULTIMA_PARCELA],
            'suspenso': [BolsistaStatus.SUSPENSO],
            'pendente': [
                BolsistaStatus.PENDENTE_GOVERNANCA,
                BolsistaStatus.AGUARDANDO_IMPLANTACAO,
            ],
        }
        if order in status_filters:
            allowed = set(status_filters[order])
            bolsistas = [b for b in bolsistas if b.check_status_validity() in allowed]
            bolsistas = sorted(bolsistas, key=lambda b: b.nome or "")
        else:
            # asc: Ativo → … → Inativo; desc: Inativo → … → Ativo.
            # Nome permanece A→Z dentro de cada grupo.
            direction = -1 if order == 'desc' else 1
            bolsistas = sorted(
                bolsistas,
                key=lambda b: (
                    status_group_order.get(b.check_status_validity(), 99) * direction,
                    b.nome or "",
                ),
            )

    elif sort_by == 'nivel':
        def nivel_key(b):
            n = (b.modalidade.nivel if b.modalidade else "").upper()
            return (n, b.nome)
        reverse = (order == 'desc')
        bolsistas = sorted(bolsistas, key=nivel_key, reverse=reverse)
        
    elif sort_by == 'edital':
        def edital_key(b):
            return b.edital.numero if b.edital and b.edital.numero else ""
        reverse = (order == 'desc')
        bolsistas = sorted(bolsistas, key=edital_key, reverse=reverse)
    
    elif sort_by == 'nome':
         bolsistas = sorted(bolsistas, key=lambda b: b.nome or "", reverse=(order=='desc'))
    
    elif sort_by == 'matricula':
        bolsistas = sorted(bolsistas, key=lambda b: b.matricula or "", reverse=(order=='desc'))

    # Stats
    from core.status_engine import BolsistaStatus
    total_registros = len(bolsistas)
    total_ativos = 0
    total_finalizando = 0
    total_inativos = 0
    total_suspenso = 0
    total_pendente = 0
    
    for b in bolsistas:
        status = b.check_status_validity()
        if status == BolsistaStatus.ATIVO:
            total_ativos += 1
        elif status in (BolsistaStatus.FINALIZANDO, BolsistaStatus.ULTIMA_PARCELA):
            total_finalizando += 1
        elif status in (BolsistaStatus.INATIVO, BolsistaStatus.CANCELAMENTO_REQUERIDO, BolsistaStatus.VENCIDO_CRITICO):
            total_inativos += 1
        elif status == BolsistaStatus.SUSPENSO:
            total_suspenso += 1
        elif status in (BolsistaStatus.PENDENTE_GOVERNANCA, BolsistaStatus.AGUARDANDO_IMPLANTACAO):
            total_pendente += 1
        else:
            total_inativos += 1
    
    resumo_niveis = {}
    for b in bolsistas:
        if b.modalidade:
            lvl = b.modalidade.nivel.strip()
            resumo_niveis[lvl] = resumo_niveis.get(lvl, 0) + 1

    return render_template('bolsistas/index.html', bolsistas=bolsistas, editais=editais, selected_edital=edital_id,
                           search_q=search_q, total_registros=total_registros,
                           total_ativos=total_ativos, total_finalizando=total_finalizando, 
                           total_inativos=total_inativos, total_suspenso=total_suspenso,
                           total_pendente=total_pendente,
                           resumo_niveis=resumo_niveis,
                           current_sort=sort_by, current_order=order,
                           total_before_filter=total_before_filter)

@bolsistas_bp.route('/bolsistas/novo', methods=['GET', 'POST'])
@require_role(['admin', 'coordenador'])
def novo():
    editais = Edital.query.all()
    campuses = Campus.query.order_by(Campus.nome).all()
    programas = ProgramaAcademico.query.join(Campus).filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa).all()

    # [NEW V10.9] Multicampi Logic
    multicampi_map = {}
    for p in programas:
        if p.codigo_programa:
            if p.codigo_programa not in multicampi_map:
                multicampi_map[p.codigo_programa] = {'siglas': set(), 'ids': set()}
            multicampi_map[p.codigo_programa]['siglas'].add(p.campus.sigla_campus)
            multicampi_map[p.codigo_programa]['ids'].add(p.campus_id)

    if request.method == 'POST':
        modalidade_id = int(request.form['modalidade_id'])
        mod = Modalidade.query.get(modalidade_id)

        # [V14.1] Vacancy Check via Service
        valid, msg = BolsistaService.validate_vacancy(modalidade_id)
        if not valid:
            flash(msg, 'error')
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None, acordos=acordos, multicampi_map=multicampi_map)

        # Calculations
        try:
            form_IC = parse_flexible_date(request.form['data_inicio_curso']) if request.form['data_inicio_curso'] else None
            ib_raw = (request.form.get('data_inicio_bolsa') or '').strip()
            dur_raw = (request.form.get('meses_duracao') or '').strip()
            form_IB = parse_flexible_date(ib_raw) if ib_raw else None
            form_D = int(dur_raw) if dur_raw else None
            form_M = mod.max_meses if mod.max_meses else 0
            
            academic_limit_months = form_M
            if mod.nivel:
                n_upper = mod.nivel.upper()
                if 'GRADUA' in n_upper or 'INICIA' in n_upper:
                    academic_limit_months = 60
                elif 'MESTR' in n_upper or 'MASTER' in n_upper:
                    academic_limit_months = 24
                elif 'DOUTOR' in n_upper or 'DOCTOR' in n_upper:
                    academic_limit_months = 48

        except ValueError:
            flash('Dados de data ou duração inválidos.', 'error')
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None, acordos=acordos, multicampi_map=multicampi_map)

        # [PI 33/2026] Governança: Início da Bolsa não pode ser anterior ao Início do Curso
        if form_IB:
            valid_gov, msg_gov = BolsistaService.validate_governance_dates({
                'data_inicio_bolsa': form_IB,
                'data_inicio_curso': form_IC
            })
            if not valid_gov:
                flash(msg_gov, 'error')
                acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
                return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None, acordos=acordos, multicampi_map=multicampi_map)

        # Limits Logic
        ext_maternity = 0 
        ext_suspension = 0
        current_afastamentos = []
        
        M_extended = academic_limit_months + ext_maternity + ext_suspension
        
        if form_IC:
            limit_date = form_IC + relativedelta(months=M_extended) - relativedelta(months=1)
        else:
            limit_date = date(2099, 12, 31)

        # [V14.1] End Date Calculation via Service
        afastamentos_input = [] # Novo bolsista não tem afastamentos prévios no form ainda
        end_date = BolsistaService.calculate_end_date(form_IB, form_D, afastamentos_input)

        if end_date:
            limit_tuple = (limit_date.year, limit_date.month)
            end_tuple = (end_date.year, end_date.month)

            if end_tuple > limit_tuple:
                # Exception Logic (Previsao Defesa)
                try:
                    pd_str = request.form.get('previsao_defesa')
                    form_PD = parse_flexible_date(pd_str) if pd_str else None
                except:
                    form_PD = None

                allow_exception = False
                if form_PD:
                    pd_tuple = (form_PD.year, form_PD.month)
                    if end_tuple <= pd_tuple:
                        allow_exception = True

                if not allow_exception:
                    flash(f'Erro de Prazo: Data Final ({end_date.strftime("%m/%Y")}) excede o limite do vínculo ({limit_date.strftime("%m/%Y")}, {academic_limit_months} meses).', 'error')
                    acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
                    return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None, acordos=acordos, multicampi_map=multicampi_map)

            if form_D and form_D > (form_M + ext_maternity):
                flash(f'Erro de Duração: {form_D} meses excede o limite da modalidade ({form_M} + {ext_maternity} bônus).', 'error')
                acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
                return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None, acordos=acordos, multicampi_map=multicampi_map)

        # Create Object
        prog_id = int(request.form['programa_id']) if request.form.get('programa_id') else None
        prog_obj = ProgramaAcademico.query.get(prog_id) if prog_id else None
        
        campus_id = int(request.form['campus_id']) if request.form.get('campus_id') else None
        campus_obj = Campus.query.get(campus_id) if campus_id else None

        campus_text = prog_obj.campus.nome if prog_obj and prog_obj.campus else (campus_obj.nome if campus_obj else request.form.get('campus', ''))
        campus_sigla = prog_obj.campus.sigla_campus if prog_obj and prog_obj.campus else (campus_obj.sigla_campus if campus_obj else get_sigla(campus_text))
        # [GOVERNANÇA] FA / FUNTEF: cadastro sem liberar pagamentos até ativação
        edital_obj = Edital.query.get(mod.edital_id)
        
        # [NEW] Padronização NAPI: Limpeza Defensiva
        instituicao_napi = request.form.get('instituicao', '').strip()
        # Logica para determinar o campus e programa linkado (Normalizado V5+)
        if instituicao_napi in VALID_NAPI:
            pass 
        else:
            prog_obj_id = prog_obj.id if prog_obj else None

        novo_bolsista = Bolsista(
            edital_id=mod.edital_id,
            modalidade_id=mod.id,
            programa_id=prog_obj_id if (instituicao_napi not in VALID_NAPI) else None,
            status_governanca='ATIVO',
            ativo=True,
            implantacao_pendente=False,
            data_fim_bolsa=end_date,
            nome=request.form['nome'],
            cpf=request.form['cpf'],
            email=request.form['email'],
            telefone=(request.form.get('telefone') or '').strip() or None,
            data_nascimento=parse_flexible_date(request.form['data_nascimento']) if request.form.get('data_nascimento') else None,
            orientador=request.form['orientador'],
            email_orientador=request.form['email_orientador'],
            data_inicio_curso=parse_flexible_date(request.form['data_inicio_curso']) if request.form['data_inicio_curso'] else None,
            previsao_defesa=parse_flexible_date(request.form['previsao_defesa']) if request.form['previsao_defesa'] else None,
            banco=request.form['banco'],
            agencia=request.form['agencia'],
            conta=request.form['conta'],
            tipo_conta=request.form['tipo_conta'],
            data_inicio_bolsa=form_IB,
            meses_duracao=form_D,
            processo_sei=request.form.get('processo_sei', ''),
            numero_formulario=request.form.get('numero_formulario', ''),
            is_pdse='is_pdse' in request.form,
            pais_destino=request.form.get('pais_destino', ''),
            projeto_pesquisa=request.form.get('projeto_pesquisa', ''),
            recebe_bolsa=request.form.get('recebe_bolsa') == '1',
            agencia_fomento=request.form.get('agencia_fomento', ''),
            tem_adicional='tem_adicional' in request.form,
            valor_adicional=clean_currency(request.form.get('valor_adicional', '0,00')),
            qtd_adicional=int(request.form.get('qtd_adicional')) if request.form.get('qtd_adicional') else 1,
            matricula=request.form.get('matricula', ''),
            instituicao=instituicao_napi,
            cidade=request.form.get('cidade', '')
        )
        novo_bolsista.edital = edital_obj
        
        caretaker = BolsistaCaretaker()
        candidatura_id_form = request.form.get('candidatura_id', type=int)
        estrategias = [AcumuloBolsaAtivaStrategy(), AcumuloProcessoSeletivoStrategy()]
        validador = ValidadorAcumuloContext(estrategias)
        erros = validador.executar_validacoes(
            novo_bolsista.cpf,
            candidatura_id_ignorar=candidatura_id_form,
        )
        has_acumulo_flag = bool(erros)

        if erros and not request.form.get('ciente_acumulo'):
            for erro in erros:
                flash(erro, 'warning')
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=novo_bolsista, has_acumulo=True, acordos=acordos, multicampi_map=multicampi_map)

        # Tratar novo comentário do histórico
        novo_comentario_texto = request.form.get('novo_comentario', '').strip()
        if novo_comentario_texto:
            comentario_obj = ComentarioBolsista(texto=novo_comentario_texto, user_id=current_user.id)
            novo_bolsista.comentarios_historico.append(comentario_obj)

        funtef_errors = _validate_funtef_fields(novo_bolsista)
        if funtef_errors:
            for err in funtef_errors:
                flash(err, 'error')
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=novo_bolsista, has_acumulo=has_acumulo_flag, acordos=acordos, multicampi_map=multicampi_map)

        _apply_funtef_fields(novo_bolsista)

        aguardando = ImplantacaoBolsaService.deve_ficar_pendente(novo_bolsista)
        if aguardando:
            ImplantacaoBolsaService.marcar_pendente(novo_bolsista, user_id=current_user.id)

        try:
            caretaker.backup(novo_bolsista)
            db.session.add(novo_bolsista)
            
            # [V14.1] Candidacy Sync via Service
            if candidatura_id_form:
                db.session.flush()
                BolsistaService.sync_candidacy(
                    candidatura_id_form, novo_bolsista.cpf, bolsista_id=novo_bolsista.id
                )

            db.session.commit()
            
            # [PHASE 2] Automação SPARKx: Disparar e-mail de onboarding
            success, msg_email = BolsistaService.trigger_sparkx_onboarding(novo_bolsista)
            if not success:
                flash(f'Atenção: {msg_email}', 'warning')
            else:
                flash('Bolsista cadastrado e e-mail SPARKx disparado!', 'success')

            _flash_funtef_result(novo_bolsista)
            if aguardando:
                flash(
                    'Cadastro salvo sem liberar pagamentos: '
                    f'{novo_bolsista.motivo_implantacao_pendente.lower()}. '
                    'Use "Ativar Bolsista (Fundação)" após Conveniar, contrato e data de liberação.',
                    'warning',
                )
                
            return redirect(url_for('bolsistas.editar', id=novo_bolsista.id, show_confirmation=1))
        except Exception as e:
            db.session.rollback()
            caretaker.undo(novo_bolsista)
            flash(f"Erro crítico no banco (Rollback acionado): {str(e)}", "error")
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=novo_bolsista, has_acumulo=has_acumulo_flag, acordos=acordos, multicampi_map=multicampi_map)

    bolsista_pre = None
    if request.method == 'GET':
        candidatura_id = request.args.get('candidatura_id', type=int)
        if candidatura_id:
            cand = Candidatura.query.get(candidatura_id)
            if cand:
                bolsista_pre = Bolsista(
                    nome=cand.nome,
                    cpf=cand.cpf,
                    email=cand.email,
                    edital_id=cand.rodada.edital_id,
                    programa_id=cand.programa_id,
                    orientador=cand.orientador,
                    email_orientador=cand.email_orientador,
                    processo_sei=cand.numero_sei,
                    projeto_pesquisa=cand.projeto_pesquisa,
                    instituicao=cand.instituicao,
                    cidade=cand.cidade
                )
        elif request.args.get('pre_nome'):
            bolsista_pre = Bolsista(
                nome=request.args.get('pre_nome', ''),
                cpf=request.args.get('pre_cpf', ''),
                email=request.args.get('pre_email', ''),
                edital_id=request.args.get('pre_edital', type=int)
            )

    return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=bolsista_pre, multicampi_map=multicampi_map)
@bolsistas_bp.route('/bolsistas/<int:id>/editar', methods=['GET', 'POST'])
@require_role(['admin', 'diretor_campus', 'coordenador_programa'])
@check_ownership(Bolsista)
def editar(id):
    bolsista = Bolsista.query.get_or_404(id)
    editais = Edital.query.all()
    campuses = Campus.query.order_by(Campus.nome).all()
    programas = ProgramaAcademico.query.filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa).all()
    
    # [NEW V10.9] Multicampi Logic
    multicampi_map = {}
    for p in programas:
        if p.codigo_programa:
            if p.codigo_programa not in multicampi_map:
                multicampi_map[p.codigo_programa] = {'siglas': set(), 'ids': set()}
            multicampi_map[p.codigo_programa]['siglas'].add(p.campus.sigla_campus if p.campus else '?')
            multicampi_map[p.codigo_programa]['ids'].add(p.campus_id)

    if request.method == 'POST':
        desligado_agora = False
        fim_anterior = bolsista.data_fim_bolsa
        # [V11.8] Memento Pattern: Granular Snapshot antes de alterações críticas
        bolsista.create_snapshot(contexto="Edição Manual via Formulário")
        
        caretaker = BolsistaCaretaker()
        caretaker.backup(bolsista)
        
        cpf = request.form['cpf']
        candidatura_id_form = request.form.get('candidatura_id', type=int)
        estrategias = [AcumuloBolsaAtivaStrategy(), AcumuloProcessoSeletivoStrategy()]
        validador = ValidadorAcumuloContext(estrategias)
        erros = validador.executar_validacoes(
            cpf,
            bolsista_id_ignorar=bolsista.id,
            candidatura_id_ignorar=candidatura_id_form,
        )
        has_acumulo_flag = bool(erros)

        if erros and not request.form.get('ciente_acumulo'):
            for erro in erros:
                 flash(erro, 'warning')
            flash("⚠️ ATENÇÃO: As alterações NÃO foram salvas. Por favor, marque a caixa 'Estou ciente do acúmulo...' no final da aba 'Vigência & Bolsa' para confirmar o cadastro.", 'danger')
            caretaker.undo(bolsista) # Remove sujeira de memória que Backup capturou
            return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais, campuses=campuses, programas=programas, has_acumulo=True, multicampi_map=multicampi_map, pagamentos_log=_pagamentos_log(bolsista))

        modalidade_id_raw = request.form.get('modalidade_id')
        if modalidade_id_raw:
            modalidade_id = int(modalidade_id_raw)
            mod = Modalidade.query.get(modalidade_id)
            bolsista.edital_id = mod.edital_id
            bolsista.modalidade_id = mod.id
        else:
            mod = bolsista.modalidade

        bolsista.nome = request.form['nome']
        bolsista.cpf = request.form['cpf']
        bolsista.email = request.form['email']
        bolsista.telefone = (request.form.get('telefone') or '').strip() or None
        dn_raw = request.form.get('data_nascimento')
        bolsista.data_nascimento = parse_flexible_date(dn_raw) if dn_raw else None
        bolsista.orientador = request.form['orientador']
        bolsista.email_orientador = request.form['email_orientador']
        bolsista.pais_origem = request.form.get('pais_origem', 'Brasil')
        bolsista.matricula = request.form.get('matricula', '') # [NEW V10.8]
        
        prog_id = int(request.form['programa_id']) if request.form.get('programa_id') else None
        campus_id = int(request.form['campus_id']) if request.form.get('campus_id') else None
        instituicao_napi = request.form.get('instituicao', '').strip()
        
        # [NEW] Padronização NAPI: Se uma instituição parceira foi selecionada, 
        # ela assume a prioridade e limpa os campos legados de vinculação acadêmica.
        
        if instituicao_napi in VALID_NAPI:
            bolsista.instituicao = instituicao_napi
            bolsista.programa_id = None
        else:
            bolsista.instituicao = instituicao_napi
            if prog_id:
                prog_obj = ProgramaAcademico.query.get(prog_id)
                if prog_obj:
                    bolsista.programa_id = prog_id
            else:
                bolsista.programa_id = None

        dic_raw = request.form.get('data_inicio_curso')
        if dic_raw:
            bolsista.data_inicio_curso = parse_flexible_date(dic_raw)
        # Se vazio (registro legado sem data de início do curso), mantém o valor atual do banco
        # sem bloquear o salvamento de outros campos (ex: nova instituição NAPI)

        bolsista.previsao_defesa = parse_flexible_date(request.form['previsao_defesa']) if request.form.get('previsao_defesa') else None

        # [PI 33/2026] Governança: Início da Bolsa não pode ser anterior ao Início do Curso
        # Validação só se aplica quando ambas as datas foram informadas
        ib_check_raw = (request.form.get('data_inicio_bolsa') or '').strip()
        if dic_raw and bolsista.data_inicio_curso and ib_check_raw:
            valid_gov, msg_gov = BolsistaService.validate_governance_dates({
                'data_inicio_bolsa': parse_flexible_date(ib_check_raw),
                'data_inicio_curso': bolsista.data_inicio_curso,
                'previsao_defesa': bolsista.previsao_defesa
            })
            if not valid_gov:
                flash(msg_gov, 'error')
                return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=bolsista, multicampi_map=multicampi_map, pagamentos_log=_pagamentos_log(bolsista))

        bolsista.banco = request.form.get('banco', bolsista.banco or '')
        bolsista.agencia = request.form.get('agencia', bolsista.agencia or '')
        bolsista.conta = request.form.get('conta', bolsista.conta or '')
        bolsista.tipo_conta = request.form.get('tipo_conta', bolsista.tipo_conta or 'corrente')

        pendente_impl = bool(
            getattr(bolsista, 'implantacao_pendente', False)
            or getattr(bolsista, 'status_governanca', None) == 'PENDENTE'
        )
        
        data_inicio_bolsa_raw = (request.form.get('data_inicio_bolsa') or '').strip()
        if data_inicio_bolsa_raw:
            nova_inicio = parse_flexible_date(data_inicio_bolsa_raw)
            if nova_inicio and nova_inicio != bolsista.data_inicio_bolsa:
                bolsista.data_inicio_bolsa = nova_inicio
                # Mantém liberação Fundação alinhada — folha Nuvem e log usam data_inicio_bolsa
                if bolsista.data_liberacao_fundacao:
                    bolsista.data_liberacao_fundacao = nova_inicio
            elif nova_inicio:
                bolsista.data_inicio_bolsa = nova_inicio
        elif pendente_impl:
            bolsista.data_inicio_bolsa = None
        
        meses_raw = (request.form.get('meses_duracao') or '').strip()
        if meses_raw:
            bolsista.meses_duracao = int(meses_raw)
        elif pendente_impl:
            bolsista.meses_duracao = None
            
        # Re-calc Logic (Simplified for brevity as it mirrors 'novo')
        form_IB = bolsista.data_inicio_bolsa
        form_D = bolsista.meses_duracao
        end_date = None
        
        # [V14.1] End Date Calculation via Service — só recalcula se tiver data de início
        if form_IB and form_D:
            afastamentos_data = [{'tipo': a.tipo, 'duracao_meses': a.duracao_meses} for a in bolsista.afastamentos]
            end_date = BolsistaService.calculate_end_date(form_IB, form_D, afastamentos_data)
            
            # Ativo ou aguardando implantação: a vigência acompanha o formulário
            if bolsista.ativo or 'ativo' in request.form or pendente_impl:
                 bolsista.data_fim_bolsa = end_date
        elif pendente_impl:
            bolsista.data_fim_bolsa = None        
        # Meta Fields
        bolsista.processo_sei = request.form.get('processo_sei', '')
        bolsista.numero_formulario = request.form.get('numero_formulario', '')
        
        # Tratar novo comentário do histórico
        novo_comentario_texto = request.form.get('novo_comentario', '').strip()
        if novo_comentario_texto:
            comentario_obj = ComentarioBolsista(texto=novo_comentario_texto, user_id=current_user.id)
            bolsista.comentarios_historico.append(comentario_obj)
            
        bolsista.is_pdse = 'is_pdse' in request.form
        bolsista.pais_destino = request.form.get('pais_destino', '')
        bolsista.cidade = request.form.get('cidade', '')
        # Deactivation Logic
        if 'ativo' not in request.form:
             # Só aciona lógica de desligamento se o bolsista estava ATIVO antes
             if bolsista.ativo:
                 desligado_agora = True
                 if bolsista.data_fim_bolsa:
                     today = date.today()
                     if bolsista.data_fim_bolsa != today:
                         bolsista.data_fim_bolsa_backup = bolsista.data_fim_bolsa
                 
                 bolsista.ativo = False
                 today = date.today()
                 if not bolsista.data_desligamento:
                     bolsista.data_desligamento = today
                 bolsista.data_fim_bolsa = today
                 if not bolsista.motivo_desligamento:
                     bolsista.motivo_desligamento = "Desligamento Manual via Sistema"
                 
                 devolucao = request.form.get('devolucao_valores')
                 bolsista.devolucao_valores = (devolucao == 'true')
                 _registrar_comentario_desligamento(bolsista, current_user.id)
             else:
                 bolsista.ativo = False
        else:
             if not bolsista.ativo:
                 if getattr(bolsista, 'implantacao_pendente', False) or bolsista.status_governanca == 'PENDENTE':
                     flash(
                         'Para liberar pagamentos de bolsa FA, use o botão '
                         '"Ativar Bolsista (Fundação)" (após Conveniar e contrato).',
                         'error',
                     )
                     acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
                     return render_template(
                         'bolsistas/form.html',
                         bolsista=bolsista, editais=editais, campuses=campuses,
                         programas=programas, acordos=acordos, multicampi_map=multicampi_map,
                         pagamentos_log=_pagamentos_log(bolsista),
                     )
                 bolsista.ativo = True
                 bolsista.data_desligamento = None
                 bolsista.ultimo_mes_email_competencia = None
                 bolsista.ultimo_mes_email_enviado_em = None
                 if bolsista.data_fim_bolsa_backup:
                     bolsista.data_fim_bolsa = bolsista.data_fim_bolsa_backup
                     bolsista.data_fim_bolsa_backup = None
                 else:
                     if end_date:
                         bolsista.data_fim_bolsa = end_date
             else:
                 bolsista.ativo = True
                 if end_date:
                     bolsista.data_fim_bolsa = end_date
             
        bolsista.tem_adicional = 'tem_adicional' in request.form
        bolsista.valor_adicional = clean_currency(request.form.get('valor_adicional', '0,00'))
        
        # [PHASE 2] Controle de Checkout
        bolsista.relatorio_entregue = 'relatorio_entregue' in request.form

        funtef_errors = _validate_funtef_fields(bolsista)
        if funtef_errors:
            for err in funtef_errors:
                flash(err, 'error')
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais, campuses=campuses, programas=programas, has_acumulo=has_acumulo_flag, acordos=acordos, multicampi_map=multicampi_map, pagamentos_log=_pagamentos_log(bolsista))

        _apply_funtef_fields(bolsista)

        qtd_adicional_raw = request.form.get('qtd_adicional')
        if qtd_adicional_raw and qtd_adicional_raw.lower() != 'none':
            bolsista.qtd_adicional = int(qtd_adicional_raw)
        else:
            bolsista.qtd_adicional = 1

        from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
        UltimoMesBolsaService.sincronizar_apos_mudanca_fim(bolsista, fim_anterior)

        try:
            log_action('UPDATE_BOLSISTA', tabela='bolsistas', registro_id=bolsista.id, detalhes=f"Nome: {bolsista.nome}")
            db.session.commit()
            _flash_funtef_result(bolsista)
            if getattr(bolsista, 'implantacao_pendente', False) or bolsista.status_governanca == 'PENDENTE':
                faltas = ImplantacaoBolsaService.pendencias(bolsista, exigir_inicio=False)
                if faltas:
                    flash(
                        'Cadastro salvo sem pagamentos. Falta para implantar: '
                        + ' '.join(faltas),
                        'warning',
                    )
                else:
                    flash(
                        'Pré-requisitos FUNTEF concluídos. Use "Ativar Bolsista (Fundação)" '
                        'com a data de liberação para liberar os pagamentos.',
                        'info',
                    )
            if desligado_agora:
                from services.relatorio_final_service import RelatorioFinalService
                ok_rel, msg_rel = RelatorioFinalService.enviar_na_desligamento(
                    bolsista, user_id=current_user.id
                )
                if ok_rel and msg_rel:
                    flash(msg_rel, 'success')
                elif msg_rel:
                    flash(msg_rel, 'warning')
            flash('✅ Cadastro Realizado com Sucesso!', 'success')
            return redirect(url_for('bolsistas.editar', id=bolsista.id, show_confirmation=1))
        except Exception as e:
            db.session.rollback()
            caretaker.undo(bolsista)
            flash(f"Erro crítico no banco (Rollback acionado): {str(e)}", "error")
            acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
            return render_template('bolsistas/form.html', bolsista=bolsista, editais=editais, campuses=campuses, programas=programas, has_acumulo=has_acumulo_flag, acordos=acordos, multicampi_map=multicampi_map, pagamentos_log=_pagamentos_log(bolsista))

    acordos = AcordoInternacional.query.filter_by(ativo=True).order_by(AcordoInternacional.pais).all()
    return render_template(
        'bolsistas/form.html',
        bolsista=bolsista,
        editais=editais,
        campuses=campuses,
        programas=programas,
        acordos=acordos,
        multicampi_map=multicampi_map,
        pagamentos_log=_pagamentos_log(bolsista),
    )

@bolsistas_bp.route('/bolsistas/<int:id>/restaurar/<int:snapshot_id>', methods=['POST'])
@require_role(['admin'])
@check_ownership(Bolsista)
def restaurar_versao(id, snapshot_id):
    """
    [V11.8] Memento Pattern: Restaura uma versão anterior do registro.
    """
    from models import BolsistaSnapshot, db
    from datetime import date
    
    bolsista = Bolsista.query.get_or_404(id)
    snapshot = BolsistaSnapshot.query.get_or_404(snapshot_id)
    
    if snapshot.bolsista_id != id:
        flash("Snapshot não pertence a este bolsista.", "error")
        return redirect(url_for('bolsistas.editar', id=id))
        
    try:
        # Ponto de Restauração de Segurança antes da reversão
        bolsista.create_snapshot(contexto=f"Snapshot reverso antes da restauração da versão {snapshot.id}")
        
        import json
        payload = json.loads(snapshot.payload) if isinstance(snapshot.payload, str) else snapshot.payload
        bolsista.nome = payload.get('nome')
        bolsista.ativo = payload.get('ativo')
        bolsista.motivo_desligamento = payload.get('motivo_desligamento')
        bolsista.meses_duracao = payload.get('meses_duracao')
        
        # Datas precisam ser convertidas de volta
        if payload.get('data_inicio_bolsa'):
            bolsista.data_inicio_bolsa = date.fromisoformat(payload['data_inicio_bolsa'])
        if payload.get('data_fim_bolsa'):
            bolsista.data_fim_bolsa = date.fromisoformat(payload['data_fim_bolsa'])
            
        db.session.commit()
        log_action('RESTORE_MEMENTO', tabela='bolsistas', registro_id=id, detalhes=f"Restaurada versão ID {snapshot_id}")
        flash('Versão restaurada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao restaurar versão: {str(e)}", "error")
        
    return redirect(url_for('bolsistas.editar', id=id))

@bolsistas_bp.route('/bolsistas/<int:id>/excluir', methods=['POST'])
@require_role(['admin', 'diretor_campus', 'coordenador_programa'])
@check_ownership(Bolsista)
def excluir(id):
    bolsista = Bolsista.query.get_or_404(id)
    is_posdoc = False
    if bolsista.modalidade and any(x in bolsista.modalidade.nivel.upper() for x in ['PÓS', 'POS', 'RESID']):
        is_posdoc = True
    db.session.delete(bolsista)
    db.session.commit()
    log_action('DELETE_BOLSISTA', tabela='bolsistas', registro_id=id, detalhes=f"Bolsista {bolsista.nome} deleted")
    flash('Registro excluído com sucesso!', 'success')
    if is_posdoc:
        return redirect(url_for('posdoc_index'))
    return redirect(url_for('bolsistas.index'))

@bolsistas_bp.route('/bolsistas/limpar_edital/<int:edital_id>', methods=['POST'])
@admin_required
def limpar_edital(edital_id):
    try:
        edital = Edital.query.get_or_404(edital_id)
        count = Bolsista.query.filter_by(edital_id=edital_id).delete()
        db.session.commit()
        log_action('DELETE_MASS', tabela='bolsistas', registro_id=edital_id, detalhes=f"Removed from Edital {edital.numero}")
        flash(f'{count} bolsistas excluídos do Edital {edital.numero}.', 'warning')
    except Exception as e:
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    return redirect(url_for('bolsistas.index', edital_id=edital_id))

@bolsistas_bp.route('/bolsistas/comentario/<int:id>/editar', methods=['POST'])
@login_required
def editar_comentario(id):
    from models import ComentarioBolsista
    comentario = ComentarioBolsista.query.get_or_404(id)
    
    # Apenas admin/gestor/master ou o autor podem editar o comentário
    if current_user.role not in ['admin', 'master', 'gestor'] and comentario.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Sem permissão para editar este comentário.'}), 403

    novo_texto = request.form.get('texto', '').strip()
    if novo_texto:
        comentario.texto = novo_texto
        comentario.atualizado_em = utc_now()
        db.session.commit()
        return jsonify({'success': True, 'texto': comentario.texto})
    return jsonify({'success': False, 'message': 'Texto não pode ser vazio.'}), 400

# --- API: VALIDATIONS ---
@bolsistas_bp.route('/api/check_matricula', methods=['GET'])
@login_required
def api_check_matricula():
    """
    [NEW V10.8] Verifica se a matrícula já existe no banco (Soft Warning).
    """
    matricula = request.args.get('matricula', '').strip()
    if not matricula:
        return jsonify({'exists': False})
    
    # Busca indexada no PostgreSQL (matricula possui index=True)
    exists = Bolsista.query.filter_by(matricula=matricula).first() is not None
    
    return jsonify({
        'exists': exists,
        'message': 'Atenção: Esta matrícula já possui um registro ativo.' if exists else ''
    })

@bolsistas_bp.route('/bolsistas/<int:id>/ativar', methods=['POST'])
@require_role(['admin', 'diretor_campus'])
def ativar(id):
    """
    [PI 33/2026] Rota de Ativação Manual (Fundação Araucária).
    """
    data_liberacao = request.form.get('data_liberacao')
    if not data_liberacao:
        flash("A Data de Liberação da Fundação é obrigatória para ativação.", "error")
        return redirect(url_for('bolsistas.editar', id=id))

    enviar_confirmacao = request.form.get('enviar_confirmacao') in ('1', 'on', 'true', 'yes')
    
    success, msg = BolsistaService.activate_bolsista(id, data_liberacao)
    if success:
        flash(msg, "success")
        if enviar_confirmacao:
            from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService
            bolsista = Bolsista.query.get(id)
            ok_mail, msg_mail = ConfirmacaoInicioBolsaService.enviar_individual(
                bolsista, user_id=current_user.id
            )
            flash(msg_mail or ('Confirmação de início enviada.' if ok_mail else 'Não foi possível enviar a confirmação.'),
                  'success' if ok_mail else 'warning')
    else:
        flash(msg, "error")
    
    return redirect(url_for('bolsistas.editar', id=id))


@bolsistas_bp.route('/bolsistas/<int:id>/preview-confirmacao-inicio', methods=['POST'])
@require_role(['admin', 'gestor', 'diretor_campus'])
@check_ownership(Bolsista)
def preview_confirmacao_inicio(id):
    """Prévia HTML do e-mail de confirmação de início (antes de ativar ou reenviar)."""
    from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService

    bolsista = Bolsista.query.get_or_404(id)
    payload = request.get_json(silent=True) or {}
    raw = (request.form.get('data_liberacao') or payload.get('data_liberacao') or '').strip()
    data_inicio = parse_flexible_date(raw) if raw else (bolsista.data_inicio_bolsa or date.today())
    if not data_inicio:
        return jsonify({'ok': False, 'error': 'Informe a data de liberação/início.'}), 400
    html, meta, subject = ConfirmacaoInicioBolsaService.render_preview_html(
        bolsista=bolsista, data_inicio=data_inicio
    )
    inicio, fim, parcelas = meta['inicio'], meta['fim'], meta['parcelas']
    aviso = None
    if not bolsista.meses_duracao:
        aviso = 'Informe os meses de duração no cadastro para calcular o fim e as parcelas.'
    return jsonify({
        'ok': True,
        'html': html,
        'subject': subject,
        'recipients': meta.get('recipients') or [],
        'cc': meta.get('cc') or [],
        'inicio': format_date_br(inicio) if inicio else None,
        'fim': format_date_br(fim) if fim else None,
        'parcelas': parcelas,
        'aviso': aviso,
    })


@bolsistas_bp.route('/bolsistas/<int:id>/reenviar-confirmacao-inicio', methods=['POST'])
@require_role(['admin', 'gestor', 'diretor_campus'])
@check_ownership(Bolsista)
def reenviar_confirmacao_inicio(id):
    """Envia/reenvia a confirmação de início (bolsista + orientador), após prévia."""
    from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService

    bolsista = Bolsista.query.get_or_404(id)
    if not bolsista.ativo or getattr(bolsista, 'implantacao_pendente', False):
        flash('A confirmação de início só se aplica a bolsistas já ativados.', 'warning')
        return redirect(url_for('bolsistas.editar', id=id))

    ok, msg = ConfirmacaoInicioBolsaService.enviar_individual(
        bolsista, forcar=True, user_id=current_user.id
    )
    flash(msg or ('Confirmação reenviada.' if ok else 'Não foi possível enviar.'), 'success' if ok else 'warning')
    return redirect(url_for('bolsistas.editar', id=id))


@bolsistas_bp.route('/bolsistas/<int:id>/reenviar-funtef', methods=['POST'])
@require_role(['admin', 'gestor', 'diretor_campus'])
@check_ownership(Bolsista)
def reenviar_funtef(id):
    """Reenvia e-mail só aos destinatários FUNTEF externos (ex.: config errada anterior)."""
    bolsista = Bolsista.query.get_or_404(id)
    if not bolsista.conveniar_cadastrado or not (bolsista.link_pasta_nuvem or '').strip():
        flash('Conveniar e link da Nuvem são necessários para reenviar à FUNTEF.', 'warning')
        return redirect(url_for('bolsistas.editar', id=id))
    if not bolsista.funtef_email_enviado_em:
        flash('Use Atualizar Cadastro para o primeiro envio FUNTEF.', 'warning')
        return redirect(url_for('bolsistas.editar', id=id))

    ok, msg = FuntefOnboardingService.reenviar_funtef_externa(bolsista, user_id=current_user.id)
    flash(msg or ('Reenviado à FUNTEF.' if ok else 'Não foi possível reenviar.'), 'success' if ok else 'warning')
    return redirect(url_for('bolsistas.editar', id=id))


@bolsistas_bp.route('/bolsistas/<int:id>/reenviar-aviso-ultimo-mes', methods=['POST'])
@require_role(['admin', 'gestor', 'diretor_campus'])
@check_ownership(Bolsista)
def reenviar_aviso_ultimo_mes(id):
    """Envia/reenvia o aviso de último mês (apenas no mês de fim da vigência)."""
    from services.ultimo_mes_bolsa_service import UltimoMesBolsaService

    bolsista = Bolsista.query.get_or_404(id)
    if not bolsista.em_ultimo_mes_bolsa:
        flash('O aviso de último mês só se aplica a bolsistas ativos no mês de término da vigência.', 'warning')
        return redirect(url_for('bolsistas.editar', id=id))

    ok, msg = UltimoMesBolsaService.enviar_aviso_individual(
        bolsista, forcar=True, user_id=current_user.id
    )
    flash(msg or ('Aviso reenviado.' if ok else 'Não foi possível reenviar o aviso.'), 'success' if ok else 'warning')
    return redirect(url_for('bolsistas.editar', id=id))


@bolsistas_bp.route('/bolsistas/<int:id>/reenviar-cobranca-relatorio', methods=['POST'])
@require_role(['admin', 'gestor', 'diretor_campus'])
@check_ownership(Bolsista)
def reenviar_cobranca_relatorio(id):
    """Envia/reenvia cobrança de relatório final (desligados sem checkout)."""
    from services.relatorio_final_service import RelatorioFinalService

    bolsista = Bolsista.query.get_or_404(id)
    if not bolsista.cobranca_relatorio_pendente:
        flash('Cobrança de relatório só se aplica a bolsistas desligados sem relatório entregue.', 'warning')
        return redirect(url_for('bolsistas.editar', id=id))

    motivo = 'mensal' if bolsista.relatorio_ultima_cobranca_em else 'desligamento'
    ok, msg = RelatorioFinalService.enviar_cobranca_individual(
        bolsista, motivo=motivo, user_id=current_user.id
    )
    flash(msg or ('Cobrança enviada.' if ok else 'Não foi possível enviar a cobrança.'), 'success' if ok else 'warning')
    return redirect(url_for('bolsistas.editar', id=id))


@bolsistas_bp.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

# --- IMPORT WORKFLOW ---
@bolsistas_bp.route('/bolsistas/importar')
def importar():
    # Placeholder for import route
    editais = Edital.query.order_by(Edital.numero.desc()).all()
    return render_template('bolsistas/importar.html', editais=editais)


# ==========================================================
# [NEW V10.9] ROTA DE SINCRONIZAÇÃO ACADÊMICA
# ==========================================================

@bolsistas_bp.route('/bolsistas/sincronizar', methods=['GET', 'POST'])
@login_required
@require_role(['gerente', 'admin'])
def sincronizar():
    """
    [V10.9] Disparador do SyncEngine: upload do CSV acadêmico + pré-visualização.
    Duas etapas:
      - GET/POST step=upload: Usuário sobe o arquivo.
      - POST step=confirm: Usuário confirma após ver o resumo de impacto.
    """
    if request.method == 'GET':
        return render_template('bolsistas/sincronizar.html')

    step = request.form.get('step', 'upload')

    if step == 'upload':
        arquivo = request.files.get('arquivo_academico')
        if not arquivo or not arquivo.filename.endswith('.csv'):
            flash('Arquivo CSV inválido.', 'danger')
            return redirect(url_for('bolsistas.sincronizar'))

        raw = arquivo.read().decode('utf-8-sig', errors='replace')
        parser = AcademicParser()
        registros = parser.parse(raw)

        # Pré-visualização de impacto (sem salvar ainda)
        # CPF usa Fernet (IV aleatório) → match via índice in-memory
        engine_preview = SyncEngine(parser=parser)
        cpf_index = engine_preview._build_cpf_index()

        matches = []
        pendentes = []
        for r in registros:
            cpf = r.get('cpf', '')
            b = cpf_index.get(cpf)
            if b:
                matches.append({'bolsista': b, 'registro_csv': r})
            else:
                pendentes.append(r)

        # Salvar CSV em arquivo temporário (evita estouro/expiração de sessão)
        import tempfile, os
        from flask import session
        tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', prefix='arandu_sync_',
            dir=current_app.config.get('UPLOAD_FOLDER', tempfile.gettempdir()),
            delete=False, encoding='utf-8'
        )
        tmp.write(raw)
        tmp.close()

        session['sync_tmp_path'] = tmp.name
        session['sync_resumo'] = {
            'total_csv': len(registros),
            'matches': len(matches),
            'pendentes': len(pendentes)
        }

        return render_template(
            'bolsistas/sincronizar.html',
            step='preview',
            matches=matches,
            pendentes=pendentes,
            resumo=session['sync_resumo']
        )

    elif step == 'confirm':
        import os
        from flask import session
        tmp_path = session.pop('sync_tmp_path', None)
        if not tmp_path or not os.path.exists(tmp_path):
            flash('Sessão expirada. Faça o upload novamente.', 'warning')
            return redirect(url_for('bolsistas.sincronizar'))

        with open(tmp_path, encoding='utf-8') as f:
            raw = f.read()

        try:
            os.remove(tmp_path)  # Limpar arquivo temporário após leitura
        except OSError:
            pass

        engine = SyncEngine(parser=AcademicParser())
        report = engine.execute(raw, contexto='Sinc. Acadêmico Março 2026')

        alertas_tit = len(report.get('alertas_titulacao', []))
        alertas_sit = len(report.get('alertas_situacao', []))

        msg = (
            f'Sincronização concluída: {report["matched"]} registros atualizados, '
            f'{report["skipped"]} pendentes de match.'
        )
        if alertas_tit:
            msg += f' | 🔴 {alertas_tit} alerta(s) de Titulação Antecipada.'
        if alertas_sit:
            msg += f' | ⚠️ {alertas_sit} bolsista(s) com situação crítica no acadêmico.'

        flash(msg, 'success' if not report['errors'] else 'warning')
        return redirect(url_for('bolsistas.conflitos'))

    return redirect(url_for('bolsistas.sincronizar'))


# ==========================================================
# [NEW V10.9] VIEW DE CONFLITOS
# ==========================================================

@bolsistas_bp.route('/bolsistas/conflitos')
@login_required
@require_role(['gerente', 'admin'])
def conflitos():
    """[V10.9] Quartel-General de Governança: exibe CPFs duplicados para resolução."""
    grupos = get_conflitos()
    alertas_titulacao = []
    for grupo in grupos:
        for b in grupo['registros']:
            if check_titulacao_conflito(b):
                alertas_titulacao.append(b)
    return render_template('bolsistas/conflitos.html', grupos=grupos, alertas_titulacao=alertas_titulacao)


# --- APIS DE RESOLUÇÃO DE CONFLITOS ---

@bolsistas_bp.route('/api/conflito/merge/<int:academic_id>/<int:capes_id>', methods=['POST'])
@login_required
@require_role(['gerente', 'admin'])
def api_conflito_merge(academic_id, capes_id):
    """[V10.9] Mescla o registro acadêmico no registro CAPES (mantém vigência)."""
    ok, msg = reconcile_merge(academic_id, capes_id)
    return jsonify({'success': ok, 'message': msg})


@bolsistas_bp.route('/api/conflito/keep/<int:keep_id>/<int:discard_id>', methods=['POST'])
@login_required
@require_role(['gerente', 'admin'])
def api_conflito_keep(keep_id, discard_id):
    """[V10.9] Mantém apenas um registro, inativando o duplicado."""
    ok, msg = reconcile_keep_one(keep_id, discard_id)
    return jsonify({'success': ok, 'message': msg})




# --- DADOS SOCIAIS ---
@bolsistas_bp.route('/bolsistas/<int:id>/dados_sociais', methods=['GET', 'POST'])
def dados_sociais(id):
    bolsista = Bolsista.query.get_or_404(id)
    social = bolsista.dados_sociais
    if request.method == 'GET':
        if not social: return jsonify({})
        return jsonify({
            'raca_cor': social.raca_cor,
            'genero_identidade': social.genero_identidade,
            'orientacao_sexual': social.orientacao_sexual,
            'pcd': social.pcd,
            'pcd_detalhe': social.pcd_detalhe,
            'etnia_origem': social.etnia_origem,
            'vinculo_comunidade': social.vinculo_comunidade,
            'lingua_materna': social.lingua_materna,
            'is_quilombola': social.is_quilombola,
            'comunidade_quilombola': social.comunidade_quilombola,
            # [NEW 2026] Campos de Refugiados e Dados Humanitários
            'is_refugiado': social.is_refugiado,
            'pais_origem_refugio': social.pais_origem_refugio,
            'status_legal_refugio': social.status_legal_refugio,
            'idioma_materno': social.idioma_materno,
            'necessidades_especificas': social.necessidades_especificas,
            #
            'ensino_medio_origem': social.ensino_medio_origem,
            'cotista_anterior': social.cotista_anterior,
            'renda_per_capita': social.renda_per_capita,
            'primeira_geracao_superior': social.primeira_geracao_superior,
            'fonte_renda': social.fonte_renda,
            'possui_dependentes': social.possui_dependentes,
            'situacao_moradia': social.situacao_moradia
        })
    if request.method == 'POST':
        data = request.json
        if not social:
            social = DadosSociais(bolsista_id=bolsista.id)
            db.session.add(social)
        
        social.raca_cor = data.get('raca_cor')
        social.genero_identidade = data.get('genero_identidade')
        social.orientacao_sexual = data.get('orientacao_sexual')
        social.pcd = data.get('pcd')
        social.pcd_detalhe = data.get('pcd_detalhe')
        social.etnia_origem = data.get('etnia_origem')
        social.vinculo_comunidade = data.get('vinculo_comunidade')
        social.lingua_materna = data.get('lingua_materna')
        social.is_quilombola = data.get('is_quilombola')
        social.comunidade_quilombola = data.get('comunidade_quilombola')
        # [NEW 2026] Campos de Refugiados e Dados Humanitários
        social.is_refugiado = data.get('is_refugiado')
        social.pais_origem_refugio = data.get('pais_origem_refugio')
        social.status_legal_refugio = data.get('status_legal_refugio')
        social.idioma_materno = data.get('idioma_materno')
        social.necessidades_especificas = data.get('necessidades_especificas')
        #
        social.ensino_medio_origem = data.get('ensino_medio_origem')
        social.cotista_anterior = data.get('cotista_anterior')
        social.renda_per_capita = data.get('renda_per_capita')
        social.primeira_geracao_superior = data.get('primeira_geracao_superior')
        social.fonte_renda = data.get('fonte_renda')
        social.possui_dependentes = data.get('possui_dependentes')
        social.situacao_moradia = data.get('situacao_moradia')
        
        try:
            bolsista.update_governance_status()
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Dados sociais salvos com sucesso!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

# --- AFASTAMENTOS ---
@bolsistas_bp.route('/bolsistas/<int:id>/afastamento/novo', methods=['POST'])
def afastamento_novo(id):
    try:
        bolsista = Bolsista.query.get_or_404(id)
        tipo = request.form['tipo']
        data_inicio = parse_flexible_date(request.form['data_inicio'])
        duracao = int(request.form['duracao_meses'])
        observacao = request.form['observacao']
        
        novo_afastamento = Afastamento(
            bolsista_id=id,
            tipo=tipo,
            data_inicio=data_inicio,
            duracao_meses=duracao,
            observacao=observacao
        )
        db.session.add(novo_afastamento)
        if bolsista.data_fim_bolsa:
            fim_anterior = bolsista.data_fim_bolsa
            bolsista.apply_extension(duracao)
            from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
            UltimoMesBolsaService.sincronizar_apos_mudanca_fim(bolsista, fim_anterior)
        
        db.session.commit()
        if bolsista.ativo:
            flash(f'Afastamento registrado. Término da bolsa estendido em {duracao} meses.', 'success')
        else:
            flash(f'Ocorrência histórica registrada (Sem alteração no término da bolsa por estar inativa).', 'info')
        return redirect(url_for('bolsistas.editar', id=id))
    except Exception as e:
        return f"Erro interno: {e}", 500

@bolsistas_bp.route('/bolsistas/afastamento/<int:id>/excluir', methods=['POST'])
def afastamento_excluir(id):
    afastamento = Afastamento.query.get_or_404(id)
    bolsista_id = afastamento.bolsista_id
    bolsista = Bolsista.query.get(bolsista_id)
    fim_anterior = bolsista.data_fim_bolsa
    bolsista.revert_extension(afastamento.duracao_meses)
    from services.ultimo_mes_bolsa_service import UltimoMesBolsaService
    UltimoMesBolsaService.sincronizar_apos_mudanca_fim(bolsista, fim_anterior)
    
    db.session.delete(afastamento)
    db.session.commit()
    flash('Afastamento removido. Data de término ajustada.', 'success')
    return redirect(url_for('bolsistas.editar', id=bolsista_id))

# --- MOBILIDADE ---
@bolsistas_bp.route('/bolsistas/<int:id>/mobilidade/novo', methods=['POST'])
def mobilidade_novo(id):
    bolsista = Bolsista.query.get_or_404(id)
    try:
        nova_mob = MobilidadeInternacional(
            bolsista_id=bolsista.id,
            pais_destino=request.form['pais_destino'],
            instituicao_destino=request.form['instituicao_destino'],
            data_inicio=parse_flexible_date(request.form['data_inicio']),
            data_fim=parse_flexible_date(request.form['data_fim']),
            tipo_mobilidade=request.form.get('tipo_mobilidade'),
            agencia_fomento=request.form.get('agencia_fomento'),
            tipo_fluxo=request.form.get('tipo_fluxo', 'saida'),
            # [NEW] Captura do vínculo com o acordo
            acordo_id = request.form.get('acordo_id') if request.form.get('acordo_id') else None
        )
        db.session.add(nova_mob)
        db.session.commit()
        flash('Registro de mobilidade adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar mobilidade: {str(e)}', 'error')
    return redirect(url_for('bolsistas.editar', id=id))

@bolsistas_bp.route('/mobilidade/<int:id>/excluir', methods=['POST'])
def mobilidade_excluir(id):
    mob = MobilidadeInternacional.query.get_or_404(id)
    bolsista_id = mob.bolsista_id
    db.session.delete(mob)
    db.session.commit()
    flash('Registro de mobilidade removido.', 'success')
    return redirect(url_for('bolsistas.editar', id=bolsista_id))

# --- DIVERSIDADE ---
@bolsistas_bp.route('/diversidade')
def diversidade():
    """
    Dashboard de Diversidade - Visualização de métricas de gênero, raça e grupos historicamente excluídos.
    """
    from collections import Counter
    from flask_login import current_user
    from utils.permissions import apply_user_scope
    
    # Query todos os dados sociais com bolsistas (incluindo inativos/egressos)
    # [V22] Filtro de Escopo Hierárquico
    query = db.session.query(DadosSociais, Bolsista).join(Bolsista)
    
    # Aplicar filtro de escopo no Bolsista
    # Precisamos filtrar pela subquery de Bolsista
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        query = query.filter(Bolsista.programa_id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        query = query.join(ProgramaAcademico).filter(
            ProgramaAcademico.campus_id == current_user.campus_id
        )
    
    dados_query = query.all()
    total = len(dados_query)
    
    if total == 0:
        return render_template('diversidade/index.html',
            total_bolsistas=0,
            stats={'mulheres': 0, 'mulheres_pct': 0, 'homens': 0, 'homens_pct': 0,
                   'pretos_pardos': 0, 'pretos_pardos_pct': 0, 'indigenas': 0, 'indigenas_pct': 0,
                   'quilombolas': 0, 'quilombolas_pct': 0, 'pcd': 0, 'pcd_pct': 0,
                   'primeira_geracao': 0, 'primeira_geracao_pct': 0},
            raca_data=[], genero_data=[], top_programas=[]
        )
    
    # Cálculos de métricas
    mulheres = sum(1 for s, _ in dados_query if s.genero_identidade and 'Mulher' in s.genero_identidade)
    homens = sum(1 for s, _ in dados_query if s.genero_identidade and 'Homem' in s.genero_identidade)
    pretos_pardos = sum(1 for s, _ in dados_query if s.raca_cor in ['Preta', 'Parda'])
    indigenas = sum(1 for s, _ in dados_query if s.raca_cor == 'Indígena')
    quilombolas = sum(1 for s, _ in dados_query if s.is_quilombola == True)
    pcd_count = sum(1 for s, _ in dados_query if s.pcd == True)
    primeira_geracao = sum(1 for s, _ in dados_query if s.primeira_geracao_superior == True)
    
    stats = {
        'mulheres': mulheres, 'mulheres_pct': (mulheres / total * 100) if total else 0,
        'homens': homens, 'homens_pct': (homens / total * 100) if total else 0,
        'pretos_pardos': pretos_pardos, 'pretos_pardos_pct': (pretos_pardos / total * 100) if total else 0,
        'indigenas': indigenas, 'indigenas_pct': (indigenas / total * 100) if total else 0,
        'quilombolas': quilombolas, 'quilombolas_pct': (quilombolas / total * 100) if total else 0,
        'pcd': pcd_count, 'pcd_pct': (pcd_count / total * 100) if total else 0,
        'primeira_geracao': primeira_geracao, 'primeira_geracao_pct': (primeira_geracao / total * 100) if total else 0,
    }
    
    # Dados para gráfico de raça/cor
    raca_counter = Counter(s.raca_cor for s, _ in dados_query if s.raca_cor)
    raca_colors = {'Branca': '#3b82f6', 'Preta': '#10b981', 'Parda': '#f59e0b', 'Amarela': '#8b5cf6', 'Indígena': '#ec4899'}
    raca_data = [{'label': k, 'count': v, 'pct': (v / total * 100), 'color': raca_colors.get(k, '#6b7280')} 
                 for k, v in raca_counter.most_common()]
    
    # Dados para gráfico de gênero
    genero_counter = Counter(s.genero_identidade for s, _ in dados_query if s.genero_identidade)
    genero_colors = {'Mulher Cis': '#ec4899', 'Mulher Trans': '#f472b6', 'Homem Cis': '#06b6d4', 
                     'Homem Trans': '#22d3ee', 'Não-binário': '#8b5cf6', 'Outros': '#6b7280'}
    genero_data = [{'label': k, 'count': v, 'pct': (v / total * 100), 'color': genero_colors.get(k, '#6b7280')} 
                   for k, v in genero_counter.most_common()]
    
    # Programas com maior diversidade (Pretos, Pardos, Indígenas, Quilombolas, PcD)
    programa_diversity = {}
    programa_total = {}
    for s, b in dados_query:
        if b.programa_link:
            prog_nome = b.programa_link.nome_programa
            campus_nome = b.programa_link.campus.nome if b.programa_link.campus else 'N/I'
            key = (prog_nome, campus_nome)
            programa_total[key] = programa_total.get(key, 0) + 1
            if s.raca_cor in ['Preta', 'Parda', 'Indígena'] or s.is_quilombola or s.pcd:
                programa_diversity[key] = programa_diversity.get(key, 0) + 1
    
    top_programas = []
    for (prog, campus), count in sorted(programa_diversity.items(), key=lambda x: x[1], reverse=True)[:10]:
        total_prog = programa_total.get((prog, campus), 1)
        top_programas.append({'nome': prog, 'campus': campus, 'count': count, 'pct': (count / total_prog * 100)})
    
    return render_template('diversidade/index.html',
        total_bolsistas=total,
        stats=stats,
        raca_data=raca_data,
        genero_data=genero_data,
        top_programas=top_programas
    )

@bolsistas_bp.route('/api/parse-bolsista', methods=['POST'])
@login_required
def parse_bolsista_api():
    """
    [V11.22] Endpoint para o Cadastro Rápido (Parsing Inteligente).
    Utiliza o StrictoSensuParser (Strategy Pattern) para extrair dados de texto.
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify(success=False, error="Nenhum texto fornecido"), 400
    
    try:
        parser = StrictoSensuParser()
        result = parser.parse(data['text'])
        
        # Log de auditoria (Saneamento v11.22)
        log_action("PARSE_AUTO", tabela="bolsistas", detalhes=f"Parsing inteligente executado para preenchimento de formulário.")
        
        return jsonify(result)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
