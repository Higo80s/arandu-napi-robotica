# Script de diagnóstico para dados do Painel Consolidado
from app import app, db
from models import ProgramaAcademico, Campus, Bolsista
from sqlalchemy import func

with app.app_context():
    print("--- Diagnóstico de Dados ---")
    
    # 1. Programas
    total_programas = ProgramaAcademico.query.count()
    print(f"Total de Programas no DB: {total_programas}")
    
    # Listar primeiros 10 nomes para ver padrão
    programas = ProgramaAcademico.query.limit(10).all()
    print("Exemplos de nomes de programas:")
    for p in programas:
        print(f" - {p.nome_programa}")
        
    # Testar filtro Mestrado/Doutorado
    mestrado = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.ilike('%MESTRADO%')).count()
    doutorado = ProgramaAcademico.query.filter(ProgramaAcademico.nome_programa.ilike('%DOUTORADO%')).count()
    print(f"Contagem Mestrado (ilike): {mestrado}")
    print(f"Contagem Doutorado (ilike): {doutorado}")
    
    # 2. Campus
    total_campus = Campus.query.count()
    print(f"Total de Campus no DB: {total_campus}")
    
    # 3. Discentes
    total_bolsistas = Bolsista.query.count()
    ativos = Bolsista.query.filter_by(ativo=True).count()
    print(f"Total Bolsistas: {total_bolsistas}")
    print(f"Bolsistas Ativos: {ativos}")
