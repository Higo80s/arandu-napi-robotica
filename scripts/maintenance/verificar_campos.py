"""
Verificar campos existentes vs necessários para o relatório
"""

from app import app
from models import ProgramaAcademico

# Campos necessários para o relatório
CAMPOS_NECESSARIOS = [
    'codigo_programa',
    'nome_programa', 
    'sigla_programa',
    'campus',  # via relação
    'niveis',
    'area_avaliacao',  # VERIFICAR
    'area_basica',     # VERIFICAR
    'ano_inicio',
    'nota_capes'
]

with app.app_context():
    # Pegar um programa de exemplo para ver os campos
    prog = ProgramaAcademico.query.first()
    
    if prog:
        print("Campos existentes no modelo ProgramaAcademico:")
        print("-" * 60)
        for attr in dir(prog):
            if not attr.startswith('_') and not callable(getattr(prog, attr)):
                valor = getattr(prog, attr)
                print(f"  {attr}: {type(valor).__name__}")
        
        print("\n" + "=" * 60)
        print("VERIFICACAO DE CAMPOS NECESSARIOS")
        print("=" * 60)
        
        tem_area_avaliacao = hasattr(prog, 'area_avaliacao')
        tem_area_basica = hasattr(prog, 'area_basica')
        
        print(f"\narea_avaliacao existe? {tem_area_avaliacao}")
        print(f"area_basica existe? {tem_area_basica}")
        
        if not tem_area_avaliacao or not tem_area_basica:
            print("\n>>> FALTAM CAMPOS! Precisa adicionar:")
            if not tem_area_avaliacao:
                print("  - area_avaliacao (String)")
            if not tem_area_basica:
                print("  - area_basica (String)")
        else:
            print("\n>>> TODOS OS CAMPOS EXISTEM!")
