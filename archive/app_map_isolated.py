from flask import Flask, render_template, jsonify, send_file
from models import db, Campus, ProgramaAcademico, Bolsista, Edital, Modalidade
from datetime import datetime
import os

# Initialize Flask App
app = Flask(__name__)

# ConfiguraÃ§Ã£o Banco de Dados (Mesma do Production)
basedir = os.path.abspath(os.path.dirname(__file__))
# Usar banco de dados de produÃ§Ã£o para leitura (READ-ONLY logic)
db_path = os.path.join(basedir, 'instance', 'gestao_editais_new.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-isolated-map-2026'

db.init_app(app)

# --- Routes Isolated for Map Development ---

@app.route('/')
def index():
    return "<h1>Ambiente Isolado de Desenvolvimento: Mapa Interativo</h1><p>Acesse: <a href='/mapa'>/mapa</a></p>"

@app.route('/mapa')
def mapa_view():
    """Renderiza a pÃ¡gina do mapa isolada."""
    return render_template('isolated_map/index.html')

@app.route('/api/campus-stats/<sigla>')
def api_campus_stats(sigla):
    """
    Retorna estatÃ­sticas do campus em JSON para o mapa.
    READ-ONLY: Apenas consultas.
    """
    try:
        sigla = sigla.upper()
        campus = Campus.query.filter_by(sigla_campus=sigla).first()
        
        if not campus:
            return jsonify({'success': False, 'error': 'Campus nÃ£o encontrado'}), 404
            
        # 1. Total de Bolsistas Ativos
        # Join: Bolsista -> Programa -> Campus
        active_count = db.session.query(Bolsista).join(Bolsista.programa_link).filter(
            ProgramaAcademico.campus_id == campus.id,
            Bolsista.ativo == True
        ).count()
        
        # 2. Total Financeiro Mensal (Estimado)
        # Soma do valor_mensal das modalidades dos bolsistas ativos
        total_mensal = db.session.query(db.func.sum(Modalidade.valor_mensal)).\
            join(Bolsista, Bolsista.modalidade_id == Modalidade.id).\
            join(ProgramaAcademico, Bolsista.programa_id == ProgramaAcademico.id).\
            filter(
                ProgramaAcademico.campus_id == campus.id,
                Bolsista.ativo == True
            ).scalar() or 0.0
            
        # 3. Lista de Programas
        programas = ProgramaAcademico.query.filter_by(campus_id=campus.id).all()
        programas_list = [p.sigla_programa for p in programas]
        
        return jsonify({
            'success': True,
            'campus': campus.nome,
            'sigla': campus.sigla_campus,
            'stats': {
                'bolsistas_ativos': active_count,
                'programas_ofertados': len(programas_list),
                'custo_mensal': total_mensal,
                'previsao_anual': total_mensal * 12, # ProjeÃ§Ã£o simples
                'lista_programas': programas_list
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dossie-campus/<sigla>')
def api_dossie_campus(sigla):
    """
    Gera e retorna o PDF do Dossiê do Campus.
    """
    try:
        from gerar_relatorio_campus_dossie import gerar_dossie_campus_pdf
        pdf_buffer = gerar_dossie_campus_pdf(sigla.upper())
        
        if not pdf_buffer:
             return "Campus não encontrado ou erro na geração.", 404
             
        return send_file(pdf_buffer, 
                         download_name=f'Dossie_Estrategico_{sigla.upper()}.pdf', 
                         mimetype='application/pdf',
                         as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("Iniciando Servidor Isolado para Mapa (Port 5004)...")
    app.run(debug=True, port=5004)
