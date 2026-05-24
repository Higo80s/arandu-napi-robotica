import sys; sys.path.insert(0,'.')
from app import app, db
from models import ProgramaAcademico, Campus, Edital
from sqlalchemy import not_
from flask import render_template
import re

with app.test_request_context('/bolsistas/novo?pre_programa_id=55&pre_campus_id=6'):
    editais = Edital.query.all()
    campuses = Campus.query.order_by(Campus.nome).all()
    programas = ProgramaAcademico.query.join(Campus).filter(not_(ProgramaAcademico.nome_programa.ilike('%*%'))).order_by(ProgramaAcademico.nome_programa).all()
    
    html = render_template('bolsistas/form.html', editais=editais, campuses=campuses, programas=programas, bolsista=None)
    
    # Check option 55
    match = re.search(r'<option[^>]*value="55"[^>]*>.*?</option>', html, re.DOTALL | re.IGNORECASE)
    if match:
        print("ENCONTROU 55:", match.group(0))
        if 'selected' in match.group(0):
            print(">>> ESTA MARCADO COMO SELECTED!")
        else:
            print(">>> NAO ESTA SELECTED!")
    else:
        print("NAO ENCONTROU O PROGRAMA 55 NO HTML!")
