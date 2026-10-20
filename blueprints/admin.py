from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, send_from_directory, jsonify
from flask_login import login_required, current_user
from models import db, ProgramaAcademico, Campus, Bolsista, Edital, Modalidade, LogAutomacao
from sqlalchemy import func, distinct, text
import pandas as pd
from io import BytesIO, StringIO
import os
import csv
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decorators import admin_required, require_role
import backup_system

admin_bp = Blueprint('admin', __name__)

def get_consolidated_stats():
    """Calcula estatísticas para o painel consolidado."""
    programas = ProgramaAcademico.query.all()
    mestrado = 0
    doutorado = 0
    
    for p in programas:
        niveis = (p.niveis or "").upper()
        nome = p.nome_programa.upper()
        is_mestrado = 'M' in niveis or 'MESTRADO' in nome or 'CIÊNCIAS' in nome
        is_doutorado = 'D' in niveis or 'DOUTORADO' in nome
        
        if is_doutorado: doutorado += 1
        if is_mestrado: mestrado += 1
            
    if mestrado == 0 and doutorado == 0:
        mestrado = len(programas)
    
    por_campus = db.session.query(Campus.nome, Campus.sigla_campus, func.count(distinct(ProgramaAcademico.id))).join(ProgramaAcademico, Campus.id == ProgramaAcademico.campus_id).group_by(Campus.id, Campus.nome, Campus.sigla_campus).all()
    
    multicampi_query = db.session.query(ProgramaAcademico.codigo_programa, func.count(distinct(Campus.id))).join(Campus, Campus.id == ProgramaAcademico.campus_id).group_by(ProgramaAcademico.codigo_programa).having(func.count(distinct(Campus.id)) > 1).all()
    
    total_discentes = Bolsista.query.count()
    ativos = Bolsista.query.filter_by(ativo=True).count()
    taxa_ativacao = (ativos / total_discentes * 100) if total_discentes > 0 else 0
    
    return {
        'total_mestrado': mestrado,
        'total_doutorado': doutorado,
        'total_geral': len(programas),
        'distribuicao_campus': por_campus,
        'programas_multicampi': multicampi_query,
        'total_discentes': total_discentes,
        'discentes_ativos': ativos,
        'taxa_ativacao': round(taxa_ativacao, 1)
    }

@admin_bp.route('/admin/consolidado')
@login_required
def admin_consolidado():
    """Painel Consolidado estatístico."""
    stats = {}
    query_programas = ProgramaAcademico.query
    
    if current_user.role == 'coordenador_programa' and current_user.programa_id:
        query_programas = query_programas.filter(ProgramaAcademico.id == current_user.programa_id)
    elif current_user.role == 'diretor_campus' and current_user.campus_id:
        query_programas = query_programas.filter(ProgramaAcademico.campus_id == current_user.campus_id)
    
    todos_programas = query_programas.all()
    
    programas_unicos_map = {}
    programas_sem_codigo = []

    for p in todos_programas:
        if p.codigo_programa and p.codigo_programa.strip():
            cod = p.codigo_programa.strip()
            if cod not in programas_unicos_map:
                programas_unicos_map[cod] = {'nome': p.nome_programa, 'niveis': p.niveis or ''}
            else:
                programas_unicos_map[cod]['niveis'] += " " + (p.niveis or '')
        else:
            programas_sem_codigo.append(p)
            
    stats['total_geral'] = len(programas_unicos_map) + len(programas_sem_codigo)
    stats['total_mestrado'] = 0
    stats['total_doutorado'] = 0
    
    def check_niveis_consolidado(nome, niveis):
        nome = (nome or '').upper()
        niveis = (niveis or '').upper()
        is_m = 'M' in niveis or 'MESTRADO' in nome or 'CIÊNCIAS' in nome
        is_d = 'D' in niveis or 'DOUTORADO' in nome
        return is_m, is_d

    for info in programas_unicos_map.values():
        is_m, is_d = check_niveis_consolidado(info['nome'], info['niveis'])
        if is_m: stats['total_mestrado'] += 1
        if is_d: stats['total_doutorado'] += 1
        
    for p in programas_sem_codigo:
        is_m, is_d = check_niveis_consolidado(p.nome_programa, p.niveis)
        if is_m: stats['total_mestrado'] += 1
        if is_d: stats['total_doutorado'] += 1
        
    if stats['total_mestrado'] == 0 and stats['total_doutorado'] == 0:
        stats['total_mestrado'] = stats['total_geral']

    campi = Campus.query.all()
    campus_stats = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69', '#2c9faf']

    for i, c in enumerate(campi):
        num_programas = ProgramaAcademico.query.filter_by(campus_id=c.id).count()
        num_ativos = db.session.query(func.count(Bolsista.id))\
            .join(ProgramaAcademico, Bolsista.programa_id == ProgramaAcademico.id)\
            .filter(ProgramaAcademico.campus_id == c.id, Bolsista.ativo == True).scalar() or 0
        pct = (num_programas / stats['total_geral'] * 100) if stats['total_geral'] > 0 else 0
        campus_stats.append({
            'id': c.id, 'nome': c.nome, 'sigla': c.sigla_campus, 'num_programas': num_programas, 
            'num_ativos': num_ativos, 'pct': pct, 'color': colors[i % len(colors)]
        })
    campus_stats.sort(key=lambda x: x['num_programas'], reverse=True)
    stats['distribuicao_campus'] = campus_stats

    from collections import defaultdict
    code_map = defaultdict(list)
    all_progs = db.session.query(ProgramaAcademico, Campus.sigla_campus).join(Campus, ProgramaAcademico.campus_id == Campus.id).all()
    for prog, sigla in all_progs:
        if prog.codigo_programa: code_map[prog.codigo_programa].append({'prog': prog, 'sigla_campus': sigla})
            
    multicampi_list = []
    for code, items in code_map.items():
        if len(items) > 1:
            total_ativos = 0
            siglas = [item['sigla_campus'] for item in items]
            nome = items[0]['prog'].nome_programa
            for item in items:
                total_ativos += Bolsista.query.filter_by(programa_id=item['prog'].id, ativo=True).count()
            multicampi_list.append({
                'codigo': code, 'nome': nome, 'siglas': ", ".join(sorted(siglas)), 
                'qtd_campus': len(items), 'total_ativos': total_ativos
            })
    stats['programas_multicampi'] = multicampi_list
    stats['discentes_ativos'] = Bolsista.query.filter_by(ativo=True).count()
    stats['total_bolsas_ofertadas'] = db.session.query(func.sum(Modalidade.vagas)).scalar() or 0
    stats['taxa_ocupacao'] = round((stats['discentes_ativos'] / stats['total_bolsas_ofertadas']) * 100, 1) if stats['total_bolsas_ofertadas'] > 0 else 0

    return render_template('admin/consolidado.html', **stats)

@admin_bp.route('/relatorios/consolidado/download')
@login_required
def download_consolidado():
    stats = get_consolidated_stats()
    df_campus = pd.DataFrame(stats['distribuicao_campus'], columns=['Campus', 'Sigla', 'Programas'])
    df_multicampi = pd.DataFrame(stats['programas_multicampi'], columns=['Código Programa', 'Qtd Campus'])
    df_resumo = pd.DataFrame([
        {'Métrica': 'Total Mestrado', 'Valor': stats['total_mestrado']},
        {'Métrica': 'Total Doutorado', 'Valor': stats['total_doutorado']},
        {'Métrica': 'Total Geral Programas', 'Valor': stats['total_geral']},
        {'Métrica': 'Total Discentes', 'Valor': stats['total_discentes']},
        {'Métrica': 'Discentes Ativos', 'Valor': stats['discentes_ativos']},
        {'Métrica': 'Taxa Ativação (%)', 'Valor': stats['taxa_ativacao']}
    ])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        df_campus.to_excel(writer, sheet_name='Por Campus', index=False)
        if not df_multicampi.empty:
            df_multicampi.to_excel(writer, sheet_name='Multicampi', index=False)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'Relatorio_Consolidado_UTFPR_{datetime.now().strftime("%Y%m%d")}.xlsx')

@admin_bp.route('/admin/programas')
@login_required
def admin_programas_lista():
    subquery_ativos = db.session.query(Bolsista.programa_id, func.count(Bolsista.id).label('ativos_count')).filter(Bolsista.ativo == True).group_by(Bolsista.programa_id).subquery()
    sort_col = request.args.get('sort', 'codigo_programa')
    sort_order = request.args.get('order', 'asc')
    query = db.session.query(ProgramaAcademico, Campus.sigla_campus, func.coalesce(subquery_ativos.c.ativos_count, 0).label('ativos_count')).join(Campus, ProgramaAcademico.campus_id == Campus.id).outerjoin(subquery_ativos, ProgramaAcademico.id == subquery_ativos.c.programa_id)
    
    orders = {
        'codigo_programa': ProgramaAcademico.codigo_programa, 'nome_programa': ProgramaAcademico.nome_programa,
        'sigla_programa': ProgramaAcademico.sigla_programa, 'campus': Campus.sigla_campus,
        'niveis': ProgramaAcademico.niveis,
        'ativos': func.coalesce(subquery_ativos.c.ativos_count, 0)
    }
    order_clause = orders.get(sort_col, ProgramaAcademico.codigo_programa)
    query = query.order_by(order_clause.desc() if sort_order == 'desc' else order_clause.asc())
    results = query.all()
    
    programas_data, programas_grad, programas_antigos = [], [], []
    campi_por_codigo = {}
    for r in results:
        if r[0].codigo_programa: campi_por_codigo[r[0].codigo_programa] = campi_por_codigo.get(r[0].codigo_programa, 0) + 1
             
    stats = {'total': 0, 'mestrado': 0, 'doutorado': 0, 'academico': 0, 'profissional': 0, 'graduacao': 0}
    for r in results:
        prog = r[0]
        item = {
            'id': prog.id, 'codigo_programa': prog.codigo_programa, 'nome_programa': prog.nome_programa,
            'sigla_programa': prog.sigla_programa, 'campus_sigla': r[1],
            'campus_count': campi_por_codigo.get(prog.codigo_programa, 1) if prog.codigo_programa else 1,
            'niveis': prog.niveis, 'ativos_count': r[2], 'instituicao': prog.campus.instituicao, 'cidade': prog.campus.cidade, 'nome_campus': prog.campus.nome
        }
        if '*' in prog.nome_programa: programas_antigos.append(item)
        elif prog.niveis == 'G':
            programas_grad.append(item)
            stats['graduacao'] += 1
        else:
            programas_data.append(item)
            stats['total'] += 1
            if 'M' in (prog.niveis or ''): stats['mestrado'] += 1
            if 'D' in (prog.niveis or ''): stats['doutorado'] += 1
            
    programas_antigos.sort(key=lambda x: x['nome_programa'])
    return render_template('admin/programas.html', programas=programas_data, programas_grad=programas_grad, programas_antigos=programas_antigos, current_sort=sort_col, current_order=sort_order, stats=stats)

@admin_bp.route('/admin/programas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_programas_editar(id):
    programa = ProgramaAcademico.query.get_or_404(id)
    campuses = Campus.query.order_by(Campus.nome).all()
    if request.method == 'POST':
        try:
            programa.nome_programa, programa.sigla_programa = request.form['nome_programa'], request.form['sigla_programa']
            programa.codigo_programa, programa.niveis = request.form['codigo_programa'], request.form['niveis']
            programa.campus_id = int(request.form['campus_id'])
            db.session.commit()
            flash('Programa atualizado com sucesso!', 'success')
            return redirect(url_for('admin.admin_programas_lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'error')
    return render_template('admin/programas_editar.html', programa=programa, campuses=campuses)

@admin_bp.route('/manual')
def manual():
    return render_template('manual.html')

@admin_bp.route('/documentacao')
def documentacao():
    return render_template('documentation.html')

@admin_bp.route('/sobre-simbolo')
def sobre_simbolo():
    return render_template('sobre_simbolo.html')

@admin_bp.route('/admin/monitor-automacao')
@login_required
@require_role(['admin', 'gestor', 'master'])
def monitor_automacao():
    logs = LogAutomacao.query.order_by(LogAutomacao.data_execucao.desc()).limit(50).all()
    return render_template('admin/monitor_automacao.html', logs=logs)

# === IMPORTAÇÃO EM MASSA ===
@admin_bp.route('/bolsistas/importar', methods=['GET', 'POST'])
@admin_required
def bolsistas_importar():
    editais = Edital.query.all()
    resultado = None

    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(request.url)
        
        file = request.files['arquivo']
        edital_id = request.form.get('edital_id')
        
        if not edital_id or file.filename == '':
            flash('Selecione um edital e um arquivo válido', 'danger')
            return redirect(request.url)

        tipo_importacao = request.form.get('tipo_importacao', 'padrao')
        is_excel = file.filename.lower().endswith(('.xlsx', '.xls'))
        csv_input = []
        
        if is_excel:
            try:
                from openpyxl import load_workbook
                wb = load_workbook(filename=file)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                if not rows:
                    flash('Arquivo Excel vazio.', 'danger')
                    return redirect(request.url)
                header = [str(h).strip() for h in rows[0] if h is not None]
                for row_idx, row_values in enumerate(rows[1:], start=2):
                    row_dict = {}
                    for i, h in enumerate(header):
                        val = row_values[i] if i < len(row_values) else None
                        row_dict[h] = str(val).strip() if val is not None else ''
                    row_dict['_line_num'] = row_idx
                    csv_input.append(row_dict)
                headers = header
            except Exception as e:
                flash(f'Erro ao ler Excel: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            file_bytes = file.stream.read()
            try:
                text_content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text_content = file_bytes.decode("latin-1")
            try:
                dialect = csv.Sniffer().sniff(text_content[:1024], delimiters='\t;,')
                delimiter = dialect.delimiter
            except:
                delimiter = ';'
            if '\t' in text_content[:100]: delimiter = '\t'
            stream = StringIO(text_content)
            reader = csv.DictReader(stream, delimiter=delimiter)
            if reader.fieldnames:
                reader.fieldnames = [f.strip().replace('\ufeff', '') for f in reader.fieldnames]
            headers = reader.fieldnames or []
            for i, row in enumerate(reader, start=1):
                row['_line_num'] = i + 1
                csv_input.append(row)

        sucesso, erros, log = 0, 0, []
        edital = Edital.query.get(edital_id)
        
        def normalize_map(items):
            m = {}
            for x in items:
                m[x.nivel.upper()] = x
                if 'DOCTOR' in x.nivel.upper() or 'DOUTOR' in x.nivel.upper(): m['DOUTORADO'] = x
                if 'MASTER' in x.nivel.upper() or 'MESTR' in x.nivel.upper(): m['MESTRADO'] = x
            return m
        modalidades_map = normalize_map(edital.modalidades)

        for row in csv_input:
            row_num = row.get('_line_num', 0)
            try:
                if tipo_importacao == 'fa':
                     novo = processar_importacao_fa(row, edital, modalidades_map, log, row_num)
                     if novo:
                         db.session.add(novo)
                         sucesso += 1
                     else: erros += 1
                elif tipo_importacao == 'posdoc':
                    # Simplified logic from app.py
                    nome = (row.get('Residente') or '').strip()
                    if not nome: raise ValueError("Campo 'Residente' obrigatório.")
                    programa = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.ilike(f"%{row.get('Programa','')}%")).first()
                    mod_posdoc = next((m for t, m in modalidades_map.items() if 'POS' in t or 'DOC' in t), edital.modalidades[0] if edital.modalidades else None)
                    novo = Bolsista(edital_id=edital.id, modalidade_id=mod_posdoc.id, programa_id=programa.id if programa else None, nome=nome, data_inicio_bolsa=date.today(), data_fim_bolsa=date.today(), meses_duracao=12, ativo=True)
                    db.session.add(novo)
                    sucesso += 1
                else:
                    # Padrao CAPES
                    vinculo = row.get('Tipo Vínculo') or row.get('Tipo Vinculo')
                    match = re.search(r'\b(\d+[A-Z]?\d+)\b', vinculo or '')
                    prog_code = match.group(1) if match else None
                    programa = ProgramaAcademico.query.filter_by(codigo_programa=prog_code).first() if prog_code else None
                    mod_text = (row.get('Modalidade') or '').strip().upper()
                    modalidade = modalidades_map.get(mod_text) or (modalidades_map.get('DOUTORADO') if 'DOUTOR' in mod_text else modalidades_map.get('MESTRADO'))
                    benef = row.get('Beneficiário') or row.get('Beneficiario') or ''
                    cpf, nome = benef.split(' - ', 1) if ' - ' in benef else (benef, 'Nome Desconhecido')
                    vigencia = row.get('Vigência') or row.get('Vigencia') or ''
                    if ' - ' in vigencia:
                        i_s, f_s = vigencia.split(' - ')
                        dt_i = datetime.strptime(i_s.strip(), '%d/%m/%Y').date()
                        dt_f = datetime.strptime(f_s.strip(), '%d/%m/%Y').date()
                        diff = relativedelta(dt_f, dt_i)
                        meses = diff.years * 12 + diff.months + (1 if diff.days > 15 else 0)
                    else: raise ValueError("Vigência inválida.")
                    novo = Bolsista(edital_id=edital.id, modalidade_id=modalidade.id, programa_id=programa.id if programa else None, nome=nome.strip(), cpf=cpf.strip(), data_inicio_bolsa=dt_i, data_fim_bolsa=dt_f, meses_duracao=meses, ativo=True)
                    db.session.add(novo)
                    sucesso += 1
            except Exception as e:
                erros += 1
                log.append(f"Linha {row_num}: {str(e)}")
        
        db.session.commit()
        resultado = {'sucesso': sucesso, 'erro': erros, 'log_erros': log}
        flash(f'Importação concluída: {sucesso} sucessos.', 'success' if sucesso > 0 else 'warning')

    return render_template('bolsistas/importar.html', editais=editais, resultado=resultado)

def processar_importacao_fa(row, edital, modalidades_map, log, row_num):
    try:
        cpf = (row.get('cpf') or '').strip()
        nome = (row.get('nome_bolsista') or '').strip()
        if not cpf: return None
        if Bolsista.query.filter_by(cpf=cpf).first(): raise ValueError(f"CPF {cpf} já existe.")
        
        mod_text = (row.get('Nível') or '').strip().upper()
        modalidade = modalidades_map.get(mod_text) or (modalidades_map.get('DOUTORADO') if 'DOUTOR' in mod_text else modalidades_map.get('MESTRADO'))
        if not modalidade: raise ValueError(f"Nível '{mod_text}' inválido.")
        
        dt_i = datetime.strptime(str(row.get('Data de Ingresso','')).strip(), '%d/%m/%Y').date() if row.get('Data de Ingresso') else date.today()
        dt_f = dt_i + relativedelta(months=12)
        
        # [NEW V11.7] New columns for FA
        sei = (row.get('numero_sei') or '').strip()
        campus_nome = (row.get('campus') or '').strip()
        projeto = (row.get('nome_projeto') or '').strip()
        
        # Sigla do campus (Helper from bolsistas_bp if available, otherwise simple logic)
        from blueprints.bolsistas import get_sigla
        sigla = get_sigla(campus_nome) if campus_nome else None

        return Bolsista(
            edital_id=edital.id, 
            modalidade_id=modalidade.id, 
            nome=nome, 
            cpf=cpf, 
            data_inicio_bolsa=dt_i, 
            data_fim_bolsa=dt_f, 
            meses_duracao=12, 
            ativo=True,
            processo_sei=sei,
            campus=campus_nome,
            campus_sigla=sigla,
            projeto_pesquisa=projeto
        )
    except Exception as e:
        log.append(f"Linha {row_num}: {str(e)}")
        return None

# === INSTITUICAO (CAMPUS) MANAGEMENT API ===
@admin_bp.route('/api/campus', methods=['POST'])
@login_required
def api_campus_create():
    try:
        data = request.json
        if not data.get('nome') or not data.get('sigla'):
            return jsonify({'success': False, 'error': 'Nome e sigla são obrigatórios'}), 400
            
        novo_campus = Campus(
            instituicao=data.get('instituicao'),
            cidade=data.get('cidade'),
            nome=data.get('nome'),
            sigla_campus=data.get('sigla')
        )
        db.session.add(novo_campus)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': novo_campus.id,
            'instituicao': novo_campus.instituicao,
            'cidade': novo_campus.cidade,
            'nome': novo_campus.nome,
            'sigla': novo_campus.sigla_campus
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# === PROGRAMA MANAGEMENT API ===
@admin_bp.route('/api/programas', methods=['POST'])
@login_required
def api_programas_create():
    try:
        data = request.json
        campus_id = int(data.get('campus_id'))
        
        novo_prog = ProgramaAcademico(
            codigo_programa=data.get('codigo') or None,
            nome_programa=data.get('nome'),
            sigla_programa=data.get('sigla'),
            campus_id=campus_id
        )
        db.session.add(novo_prog)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': novo_prog.id,
            'nome': novo_prog.nome_programa,
            'sigla': novo_prog.sigla_programa,
            'campus_id': novo_prog.campus_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_bp.route('/api/programas/<int:id>', methods=['GET'])
@login_required
def api_programas_get(id):
    prog = ProgramaAcademico.query.get_or_404(id)
    return jsonify({
        'id': prog.id,
        'codigo': prog.codigo_programa,
        'nome': prog.nome_programa,
        'sigla': prog.sigla_programa,
        'campus_id': prog.campus_id
    })

@admin_bp.route('/api/programas/<int:id>', methods=['PUT'])
@login_required
def api_programas_update(id):
    try:
        prog = ProgramaAcademico.query.get_or_404(id)
        data = request.json
        
        prog.codigo_programa = data.get('codigo') or None
        prog.nome_programa = data.get('nome')
        prog.sigla_programa = data.get('sigla')
        prog.campus_id = int(data.get('campus_id'))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': prog.id,
            'nome': prog.nome_programa,
            'sigla': prog.sigla_programa,
            'campus_id': prog.campus_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# === DOCUMENTATION ===
@admin_bp.route('/docs/download/<filename>')
@login_required
def docs_download(filename):
    """Serve documentation PDFs from static/docs folder"""
    try:
        # app.root_path requires current_app
        from flask import current_app
        docs_dir = os.path.join(current_app.root_path, 'static', 'docs')
        return send_from_directory(docs_dir, filename, as_attachment=True)
    except FileNotFoundError:
        flash('Arquivo de documentação não encontrado.', 'error')
        return redirect(url_for('index'))

@admin_bp.route('/admin/backup', methods=['POST'])
@login_required
def admin_backup():
    """Cria backup completo: código + banco PostgreSQL/SQLite"""
    try:
        from flask import current_app
        backup_path = backup_system.create_backup(flask_app=current_app._get_current_object())
        
        if backup_path:
            cloud_destination = backup_system.copy_to_cloud(backup_path)
            backup_system.clean_old_backups(backup_system.BACKUP_DIR)
            
            msg = "✅ Backup completo realizado! Inclui código + banco de dados."
            if cloud_destination:
                msg += f" Cópia na Nuvem: {cloud_destination}"
            
            flash(msg, 'success')
            return send_file(backup_path, as_attachment=True, download_name=os.path.basename(backup_path))
        else:
            flash('Erro ao criar backup local. Verifique o console.', 'danger')
            
    except Exception as e:
        flash(f'Erro crítico no backup: {str(e)}', 'danger')
        
@admin_bp.route('/admin/health-check')
@login_required
@admin_required
def health_check():
    """
    [V11.13] Dashboard de Integridade e Saúde do Legado.
    """
    from core.status_engine import StatusEngine
    
    # 1. State Sync (Busca vs Cadastro)
    # No Arandú v11.8, o status é dinâmico. Validamos inconsistências.
    bolsistas = Bolsista.query.all()
    inconsistencias = []
    sync_count = 0
    
    for b in bolsistas:
        status_calculado = b.check_status_validity()
        # Se bolsista.ativo for True mas o status calculado for INATIVO (ex: vencido)
        # e não houver licença/prorrogação, é uma inconsistência de dashboard.
        if b.ativo and status_calculado == 'INATIVO':
            # Verifica se há licença ativa (StatusEngine já faz isso, mas aqui logamos)
            inconsistencias.append(b)
        else:
            sync_count += 1
            
    # 2. Cobertura de Memento
    from models import BolsistaSnapshot
    total_snaps = BolsistaSnapshot.query.count()
    
    # 3. Integridade do Legado (IDs < 100)
    legado = Bolsista.query.filter(Bolsista.id < 100).order_by(Bolsista.id.asc()).all()
    legado_erros = [b for b in legado if not b.data_fim_bolsa or not b.cpf]
    
    # 4. Fila de Saneamento
    try:
        fila_saneamento = Bolsista.query.filter(Bolsista.processo_sei == 'pendente_manual').all()
    except:
        fila_saneamento = []

    return render_template('admin/health_check.html',
        total_bolsistas=len(bolsistas),
        sync_count=sync_count,
        inconsistencias=inconsistencias,
        total_snaps=total_snaps,
        legado=legado,
        legado_erros=legado_erros,
        fila_saneamento=fila_saneamento
    )

@admin_bp.route('/admin/health-check/fix-states', methods=['POST'])
@login_required
@admin_required
def fix_states():
    """
    [V11.13] Auto-Cura: Recalcula o status de todos os bolsistas venciada.
    """
    from core.status_engine import StatusEngine
    from datetime import date
    
    bolsistas = Bolsista.query.filter_by(ativo=True).all()
    fixed = 0
    today = date.today()
    
    for b in bolsistas:
        if b.data_fim_bolsa and b.data_fim_bolsa < today:
            # Verifica se tem licença antes de desativar
            status = b.check_status_validity()
            if status == 'INATIVO':
                b.create_snapshot(contexto="Auto-Cura: Desativação automática por vencimento sem licença.")
                b.ativo = False
                if not b.data_desligamento:
                    b.data_desligamento = b.data_fim_bolsa
                fixed += 1
                
    db.session.commit()
    log_action('HEALTH_CHECK_FIX', tabela='bolsistas', detalhes=f"{fixed} registros corrigidos automaticamente.")
    flash(f"Processo concluído: {fixed} bolsistas atualizados para Inativo com base na vigência real.", "success")
    return redirect(url_for('admin.health_check'))

@admin_bp.route('/admin/health-check/download-report')
@login_required
@admin_required
def download_legacy_report():
    """
    [V11.13] Gera relatório Excel de integridade do legado.
    """
    from core.status_engine import StatusEngine
    
    bolsistas = Bolsista.query.all()
    data = []
    
    for b in bolsistas:
        status_calculado = b.check_status_validity()
        has_snap = b.snapshots.count() > 0
        is_legacy = b.id < 100
        
        data.append({
            'ID': b.id,
            'Nome': b.nome,
            'CPF': b.cpf if b.cpf else 'FALTANTE',
            'Ativo (BD)': 'SIM' if b.ativo else 'NÃO',
            'Status (Motor)': status_calculado,
            'Legado (<100)': 'SIM' if is_legacy else 'NÃO',
            'Sincronizado': 'SIM' if (b.ativo and status_calculado != 'INATIVO') or (not b.ativo and status_calculado == 'INATIVO') else 'NÃO',
            'Memento Coverage': 'SIM' if has_snap else 'NÃO'
        })
        
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Integridade Arandú v12.0', index=False)
    output.seek(0)
    
    filename = f"Relatorio_Saude_Arandu_{date.today().strftime('%Y%m%d')}.xlsx"
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)


@admin_bp.route('/admin/config-funtef', methods=['GET', 'POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_funtef():
    from services.funtef_onboarding_service import FuntefOnboardingService

    if request.method == 'POST':
        ok, msg = FuntefOnboardingService.save_config(
            request.form.get('funtef_emails', ''),
            request.form.get('funtef_email_corpo', ''),
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('admin.config_funtef'))

    return render_template(
        'admin/config_funtef.html',
        emails_raw='; '.join(FuntefOnboardingService.get_funtef_external_recipients()),
        corpo_raw=FuntefOnboardingService.get_email_body_raw(),
        preview_html=FuntefOnboardingService.render_preview_html(),
    )


@admin_bp.route('/admin/config-funtef/preview', methods=['POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_funtef_preview():
    """Prévia AJAX do HTML do e-mail FUNTEF (dados de exemplo)."""
    from services.funtef_onboarding_service import FuntefOnboardingService
    corpo = request.form.get('corpo', '')
    html = FuntefOnboardingService.render_preview_html(corpo_text=corpo)
    return jsonify({'html': html})


@admin_bp.route('/admin/config-relatorio-final', methods=['GET', 'POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_relatorio_final():
    from services.relatorio_final_service import RelatorioFinalService

    if request.method == 'POST':
        ok, msg = RelatorioFinalService.save_config(
            request.form.get('email_corpo', ''),
            request.form.get('equipe_emails', ''),
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('admin.config_relatorio_final'))

    return render_template(
        'admin/config_relatorio_final.html',
        corpo_raw=RelatorioFinalService.get_email_body_raw(),
        equipe_raw=RelatorioFinalService.get_equipe_email_raw(),
    )


@admin_bp.route('/admin/config-ultimo-mes-bolsa', methods=['GET', 'POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_ultimo_mes_bolsa():
    from services.ultimo_mes_bolsa_service import UltimoMesBolsaService

    if request.method == 'POST':
        ok, msg = UltimoMesBolsaService.save_config(
            request.form.get('email_corpo', ''),
            request.form.get('equipe_emails', ''),
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('admin.config_ultimo_mes_bolsa'))

    return render_template(
        'admin/config_ultimo_mes_bolsa.html',
        corpo_raw=UltimoMesBolsaService.get_email_body_raw(),
        equipe_raw=UltimoMesBolsaService.get_equipe_email_raw(),
    )


@admin_bp.route('/admin/config-confirmacao-inicio', methods=['GET', 'POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_confirmacao_inicio():
    from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService

    if request.method == 'POST':
        ok, msg = ConfirmacaoInicioBolsaService.save_config(
            request.form.get('email_corpo', ''),
            request.form.get('equipe_emails', ''),
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('admin.config_confirmacao_inicio'))

    preview_html, _meta, _subject = ConfirmacaoInicioBolsaService.render_preview_html()
    return render_template(
        'admin/config_confirmacao_inicio.html',
        corpo_raw=ConfirmacaoInicioBolsaService.get_email_body_raw(),
        equipe_raw=ConfirmacaoInicioBolsaService.get_equipe_email_raw(),
        preview_html=preview_html,
    )


@admin_bp.route('/admin/config-confirmacao-inicio/preview', methods=['POST'])
@login_required
@require_role(['admin', 'gestor'])
def config_confirmacao_inicio_preview():
    from services.confirmacao_inicio_bolsa_service import ConfirmacaoInicioBolsaService
    corpo = request.form.get('corpo', '')
    html, _meta, _subject = ConfirmacaoInicioBolsaService.render_preview_html(corpo_text=corpo)
    return jsonify({'html': html})


@admin_bp.route('/admin/automacoes')
@login_required
@require_role(['admin', 'gestor', 'master'])
def automacoes_hub():
    """Central de automações — status + atalhos (não gerencia o Task Scheduler)."""
    from services.automacoes_hub_service import build_hub
    return render_template('admin/automacoes_hub.html', **build_hub())


@admin_bp.route('/admin/config-pagamento-bolsas', methods=['GET', 'POST'])
@login_required
@require_role(['admin', 'gestor', 'master'])
def config_pagamento_bolsas():
    from services.pagamento_email_service import PagamentoEmailService

    if request.method == 'POST' and request.form.get('action') == 'salvar':
        ok, msg = PagamentoEmailService.save_config(
            request.form.get('email_corpo', ''),
            request.form.get('equipe_emails', ''),
        )
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('admin.config_pagamento_bolsas'))

    mes_ref = request.args.get('mes') or PagamentoEmailService.default_mes()
    preview_html, meta = PagamentoEmailService.render_preview_html(mes_yyyy_mm=mes_ref)
    return render_template(
        'admin/config_pagamento_bolsas.html',
        corpo_raw=PagamentoEmailService.get_email_body_raw(),
        equipe_raw=PagamentoEmailService.get_equipe_email_raw(),
        preview_html=preview_html,
        meta=meta,
        mes_ref=mes_ref,
    )


@admin_bp.route('/admin/config-pagamento-bolsas/preview', methods=['POST'])
@login_required
@require_role(['admin', 'gestor', 'master'])
def config_pagamento_bolsas_preview():
    from services.pagamento_email_service import PagamentoEmailService
    corpo = request.form.get('corpo', '')
    mes = request.form.get('mes') or PagamentoEmailService.default_mes()
    html, _meta = PagamentoEmailService.render_preview_html(mes_yyyy_mm=mes, corpo_text=corpo)
    return jsonify({'html': html})


@admin_bp.route('/admin/config-pagamento-bolsas/disparar', methods=['POST'])
@login_required
@require_role(['admin', 'gestor', 'master'])
def config_pagamento_bolsas_disparar():
    from services.pagamento_email_service import PagamentoEmailService

    mes = (request.form.get('mes') or '').strip() or PagamentoEmailService.default_mes()
    ok, msg = PagamentoEmailService.disparar(mes_yyyy_mm=mes, forcar=True)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('admin.config_pagamento_bolsas', mes=mes))
