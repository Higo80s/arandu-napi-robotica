"""
Script 4: Verificar PPGFCET no dropdown
Testa visibilidade do programa nos formulários
"""

from app import app
from models import ProgramaAcademico

with app.app_context():
    print("=== VERIFICANDO PPGFCET ===\n")
    
    programas = ProgramaAcademico.query.filter_by(codigo_programa='40006018019P8').all()
    
    if programas:
        print(f"Encontrados: {len(programas)} registros\n")
        
        for p in programas:
            print(f"ID {p.id}: {p.nome_programa}")
            print(f"  Sigla: {p.sigla_programa}")
            print(f"  Codigo: {p.codigo_programa}")
            print(f"  Campus: {p.campus.nome if p.campus else 'SEM CAMPUS'}")
            print(f"  Campus ID: {p.campus_id}")
            print(f"  Niveis: {p.niveis}")
            
            # Verificar se níveis está correto
            if not p.niveis or p.niveis == 'None':
                print(f"\n  ⚠️  PROBLEMA: Campo niveis vazio!")
                print(f"  Corrigir para: 'MP,DP' (Mestrado e Doutorado Profissional)")
            else:
                print(f"\n  ✅ Campo niveis OK")
                print(f"  Deve aparecer em dropdowns para modalidades: {p.niveis}")
    else:
        print("❌ PPGFCET NAO ENCONTRADO no banco de dados!")
        print("Necessario cadastrar o programa:")
        print("  Codigo: 40006018019P8")
        print("  Nome: Formacao Cientifica, Educacional e Tecnologica")
        print("  Sigla: PPGFCET")
        print("  Campus: Curitiba (CT)")
        print("  Niveis: MP,DP")
