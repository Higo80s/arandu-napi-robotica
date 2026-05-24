
# COPIED FROM app.py AND MODIFIED FOR ISOLATED TESTING

import os
import csv
import io
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, send_from_directory
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from models import db, Edital, Modalidade, Campus, ProgramaAcademico, Bolsista, Afastamento, Acompanhamento, Residente
import re

app = Flask(__name__)

# --- TEST CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'test_vagas.db') # CHANGED DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test_secret'
db.init_app(app)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('dashboard.html')

# Dummy Routes to satisfy url_for in templates
@app.route('/editais')
def editais_index(): return "Dummy Editais"

@app.route('/editais/<int:id>/modalidades')
def modalidades_gerenciar(id): return "Dummy Modalidades"

@app.route('/alertas')
def alertas_index(): return "Dummy Alertas"

@app.route('/bolsistas/importar')
def bolsistas_importar(): return "Dummy Importar"

@app.route('/posdoc')
def posdoc_index(): return "Dummy PosDoc"

@app.route('/capes/dashboard')
def capes_dashboard(): return "Dummy CAPES"

@app.route('/relatorios')
def relatorios_index(): return "Dummy Relatorios"

@app.route('/tutorial')
def tutorial(): return "Dummy Tutorial"

@app.route('/docs/download/<filename>')
def docs_download(filename): return "Dummy Docs"

@app.route('/admin/backup', methods=['POST'])
def admin_backup(): return "Dummy Backup"

# [NEW] Context Processor for Sidebar Badges (Fixing another potential error)
@app.context_processor
def inject_alerts():
    return dict(total_alerts=0)


@app.route('/bolsistas')
def bolsistas_index():
    bolsistas = Bolsista.query.all()
    # Dummy data needed for template
    total_registros = len(bolsistas)
    total_ativos = len([b for b in bolsistas if b.ativo])
    return render_template('bolsistas/index.html', bolsistas=bolsistas, editais=[], 
                           total_registros=total_registros, total_ativos=total_ativos,
                           total_finalizando=0, total_inativos=0, total_graduacao=0,
                           total_mestrado=0, total_doutorado=0, total_posdoc=0,
                           search_q='', current_sort='nome', current_order='asc', total_before_filter=total_registros)

@app.route('/bolsistas/novo', methods=['GET', 'POST'])
def bolsistas_novo():
    editais = Edital.query.all()
    campuses = Campus.query.all()
    programas = ProgramaAcademico.query.all()

    if request.method == 'POST':
        modalidade_id = int(request.form['modalidade_id'])
        mod = Modalidade.query.get(modalidade_id)

        # [NEW Logic: Check Vacancy Limit]
        occupied = 0
        for b in mod.bolsistas:
             # Use simple active check for test simplicity or replicate full logic
             if b.ativo and (not b.data_fim_bolsa or b.data_fim_bolsa >= date.today()):
                 occupied += 1
        
        if occupied >= mod.vagas:
            flash(f'Erro: Limite de Vagas Esgotado! Esta modalidade possui {mod.vagas} vagas e todas estão ocupadas.', 'error')
            # Render template with error
            return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None)

        # ... (rest of creation logic simplified for test) ...
        
        try:
             # Minimal creation for test
             novo = Bolsista(
                 edital_id=mod.edital_id,
                 modalidade_id=mod.id,
                 nome=request.form['nome'],
                 cpf=request.form['cpf'],
                 data_inicio_bolsa=datetime.strptime(request.form['data_inicio_bolsa'], '%Y-%m-%d').date(),
                 meses_duracao=12,
                 data_fim_bolsa=date(2025, 12, 31),
                 ativo=True
             )
             db.session.add(novo)
             db.session.commit()
             flash('Bolsista cadastrado com sucesso!', 'success')
             return redirect(url_for('bolsistas_index'))
        except Exception as e:
             flash(f'Erro: {str(e)}', 'error')
    
    return render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None)

# --- API FOR DYNAMIC SELECTS (Required for Form) ---
@app.route('/api/modalidades/<int:edital_id>')
def api_modalidades(edital_id):
    modalidades = Modalidade.query.filter_by(edital_id=edital_id).all()
    return jsonify([{
        'id': m.id, 
        'nivel': m.nivel, 
        'valor': m.valor_mensal, 
        'vagas': m.vagas,
        'max_meses': m.max_meses
    } for m in modalidades])

if __name__ == '__main__':
    # Run on different port to avoid conflict
    app.run(debug=True, port=5001)
