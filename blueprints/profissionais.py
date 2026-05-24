from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from models import db, ProgramaAcademico, Bolsista, Edital, AgenciaFomento
from sqlalchemy import func, not_
import hashlib

profissionais_bp = Blueprint('profissionais', __name__, url_prefix='/profissionais')

def format_currency_br(value):
    try:
        if value is None:
            return "0,00"
        return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

@profissionais_bp.route('/')
@login_required
def dashboard():
    """
    Dashboard Principal de Captação P&D - Programas Profissionais
    """
    # 1. Obter todos os programas profissionais
    programas_mpdp = ProgramaAcademico.query.filter(
        ProgramaAcademico.tipo_oferta == 'Profissional',
        not_(ProgramaAcademico.nome_programa.ilike('%*%')) # Exclui legados
    ).all()
    
    programa_ids = [p.id for p in programas_mpdp]
    
    if not programa_ids:
        # Fallback caso não haja programas classificados como profissionais ainda
        flash("Nenhum programa profissional cadastrado no sistema base.", "info")
        stats = {
            'total_captado': 0, 'bolsistas_ativos': 0, 'parcerias_ativas': 0
        }
        return render_template('profissionais/dashboard.html', stats=stats)

    # 2. Estatísticas Gerais (KPIs)
    # Bolsistas vigentes vinculados a esses programas
    bolsistas_ativos = Bolsista.query.filter(
        Bolsista.programa_id.in_(programa_ids),
        Bolsista.ativo == True
    ).count()

    # Editais/Acordos (que financiaram os bolsistas ou possuem orçamento total atrelado ao programa)
    # Consideramos editais onde ao menos um bolsista destes programas está alocado, ou se for possível linkar direto.
    # Por praticidade da V25, olhamos para a soma do orcamento_total dos editais que financiaram estes bolsistas.
    editais_financiadores = db.session.query(Edital).join(Bolsista).filter(
        Bolsista.programa_id.in_(programa_ids),
    ).distinct().all()

    total_captado = sum([(e.orcamento_total or 0) for e in editais_financiadores])
    parcerias_ativas = len([e for e in editais_financiadores if not e.prestacao_contas])

    stats = {
        'total_captado': format_currency_br(total_captado),
        'bolsistas_ativos': bolsistas_ativos,
        'parcerias_ativas': parcerias_ativas
    }

    # 3. Gráfico (Estilo Barras do Internacionalização) - Captação por Agência
    # Top Agências Financiadoras (Baseado na contagem de bolsistas ativos e/ou orcamento total)
    agencias_raw = db.session.query(
        AgenciaFomento.nome, 
        func.count(Bolsista.id).label('qtd_bolsistas')
    ).join(Edital, Edital.agencia_id == AgenciaFomento.id)\
     .join(Bolsista, Bolsista.edital_id == Edital.id)\
     .filter(Bolsista.programa_id.in_(programa_ids), Bolsista.ativo == True)\
     .group_by(AgenciaFomento.nome)\
     .order_by(func.count(Bolsista.id).desc())\
     .limit(5).all()

    # Se a foreign_key direta estiver falhando, falback para a string lega 'agencia' de Edital
    if not agencias_raw:
        agencias_raw = db.session.query(
            Edital.agencia, 
            func.count(Bolsista.id).label('qtd_bolsistas')
        ).join(Bolsista, Bolsista.edital_id == Edital.id)\
         .filter(Bolsista.programa_id.in_(programa_ids), Bolsista.ativo == True)\
         .group_by(Edital.agencia)\
         .order_by(func.count(Bolsista.id).desc())\
         .limit(5).all()

    # Consolidate raw agencies into acronym groups
    agencias_consolidadas = {}
    for nome, count in agencias_raw:
        raw_lower = (nome or 'UTFPR').lower()
        if 'capes' in raw_lower or 'coordena' in raw_lower:
            grupo = 'CAPES'
        elif 'cnpq' in raw_lower or 'conselho' in raw_lower:
            grupo = 'CNPq'
        elif 'fa' in raw_lower or 'arauc' in raw_lower:
            grupo = 'FA'
        elif 'rp' in raw_lower or 'receita' in raw_lower or 'próprio' in raw_lower or 'institucional' in raw_lower or 'utfpr' in raw_lower:
            grupo = 'RP'
        else:
            grupo = nome or 'Outros'
            
        agencias_consolidadas[grupo] = agencias_consolidadas.get(grupo, 0) + count

    # Sort groups by count descending
    sorted_agencias = sorted(agencias_consolidadas.items(), key=lambda x: x[1], reverse=True)[:5]

    top_agencias = []
    total_agencias = sum(agencias_consolidadas.values())
    
    def get_color(text):
        # Determistic pastel color generator based on text
        import hashlib
        h = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        r = (h & 0xFF) % 128 + 127      # Keep colors light/pastel
        g = ((h >> 8) & 0xFF) % 128 + 127
        b = ((h >> 16) & 0xFF) % 128 + 127
        return f"#{r:02x}{g:02x}{b:02x}"

    for nome, count in sorted_agencias:
        pct = (count / total_agencias * 100) if total_agencias > 0 else 0
        top_agencias.append({
            'label': nome,
            'count': count,
            'pct': pct,
            'color': get_color(nome)
        })

    # Lista de Bolsistas para a Tabela de Detalhamento
    bolsistas_lista = Bolsista.query.filter(
        Bolsista.programa_id.in_(programa_ids)
    ).order_by(Bolsista.ativo.desc(), Bolsista.data_inicio_bolsa.desc()).limit(100).all()

    def ag_sigla(raw_name):
        if not raw_name: return "ND"
        lower_name = raw_name.lower()
        if 'capes' in lower_name or 'coordena' in lower_name or 'aperfei' in lower_name:
            return 'CAPES'
        if 'cnpq' in lower_name or 'conselho' in lower_name or 'nacional de desenvolvimento cient' in lower_name:
            return 'CNPq'
        if 'fa' in lower_name or 'arauc' in lower_name:
            return 'FA'
        if 'rp' in lower_name or 'receita' in lower_name or 'próprio' in lower_name or 'pr' in lower_name and 'prio' in lower_name or 'utfpr' in lower_name or 'institucional' in lower_name:
            return 'RP'
        return raw_name

    return render_template('profissionais/dashboard.html', 
                           stats=stats, 
                           top_agencias=top_agencias,
                           bolsistas=bolsistas_lista,
                           ag_sigla=ag_sigla)
