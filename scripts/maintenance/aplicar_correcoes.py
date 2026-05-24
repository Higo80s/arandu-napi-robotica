"""
Aplicação de TODAS as correções informadas pelo usuário
"""

from app import app, db
from models import ProgramaAcademico, Campus
from sqlalchemy import text

with app.app_context():
    print("=" * 80)
    print("APLICANDO CORRECOES")
    print("=" * 80)
    
    campus_dict = {c.sigla_campus: c for c in Campus.query.all()}
    
    # BLOCO 1: Padronizar graduação
    print("\n1. PADRONIZANDO CURSOS DE GRADUACAO")
    print("-" * 80)
    
    graduacao_map = [
        {"old": "CC-TD(grad)", "codigo": "GRAD-CC-TD", "nome": "Ciencia da Computacao", "sigla": "CC-GRAD", "campus": "TD"},
        {"old": "00", "codigo": "GRAD-ELEO-TD-1", "nome": "Engenharia Eletronica", "sigla": "ELEO-GRAD", "campus": "TD"},
        {"old": "EEL(grad)", "codigo": "GRAD-EEL-PG", "nome": "Engenharia Eletrica", "sigla": "EEL-GRAD", "campus": "PG"},
        {"old": "0000", "codigo": "GRAD-ELEO-PG", "nome": "Engenharia Eletronica", "sigla": "ELEO-GRAD", "campus": "PG"},
        {"old": "EEO(grad)", "codigo": "GRAD-ELEO-TD-2", "nome": "Engenharia Eletronica", "sigla": "ELEO-GRAD", "campus": "TD"},
    ]
    
    for item in graduacao_map:
        prog = ProgramaAcademico.query.filter_by(codigo_programa=item['old']).first()
        if prog:
            prog.codigo_programa = item['codigo']
            prog.nome_programa = f"{item['nome']} (Graduacao)"
            prog.sigla_programa = item['sigla']
            prog.campus_id = campus_dict[item['campus']].id
            prog.niveis = "GRAD"
            prog.nota_capes = None
            print(f"  [{item['old']}] -> {item['codigo']}")
    
    db.session.commit()
    print("  OK - Graduacao padronizada")
    
    # BLOCO 2: Corrigir PPGECT Doutorado
    print("\n2. CORRIGINDO PPGECT DOUTORADO")
    print("-" * 80)
    
    ppgect_dout = ProgramaAcademico.query.filter_by(codigo_programa='40006018028P7').first()
    if ppgect_dout:
        ppgect_dout.nome_programa = "ENSINO DE CIENCIA E TECNOLOGIA"
        ppgect_dout.niveis = "D"
        print(f"  [40006018028P7] Nome corrigido, niveis=D")
    db.session.commit()
    
    # BLOCO 3: Verificar/Criar PPGECT Mestrado
    print("\n3. VERIFICANDO PPGECT MESTRADO")
    print("-" * 80)
    
    ppgect_mest = ProgramaAcademico.query.filter_by(codigo_programa='40006018006P3').first()
    if ppgect_mest:
        ppgect_mest.nome_programa = "ENSINO DE CIENCIA E TECNOLOGIA"
        ppgect_mest.niveis = "MP"
        ppgect_mest.nota_capes = "5"
        ppgect_mest.ano_inicio = 2008
        print(f"  [40006018006P3] Atualizado - Mestrado Profissional")
    else:
        print(f"  [40006018006P3] NAO ENCONTRADO - precisa criar manualmente")
    db.session.commit()
    
    # BLOCO 4: Corrigir PPGIT niveis
    print("\n4. CORRIGINDO PPGIT NIVEIS")
    print("-" * 80)
    
    ppgit = ProgramaAcademico.query.filter_by(codigo_programa='40006018170P8').first()
    if ppgit:
        ppgit.niveis = "MP"
        print(f"  [40006018170P8] Niveis: 'M,MP' -> 'MP'")
    db.session.commit()
    
    # BLOCO 5: Excluir duplicatas
    print("\n5. EXCLUINDO DUPLICATAS")
    print("-" * 80)
    
    dup1 = ProgramaAcademico.query.filter_by(codigo_programa='33004010001P1').first()
    if dup1:
        db.session.delete(dup1)
        print(f"  [33004010001P1] PPGEM-AP duplicata EXCLUIDO")
    
    dup2 = ProgramaAcademico.query.filter_by(codigo_programa='33004030001P1').first()
    if dup2:
        db.session.delete(dup2)
        print(f"  [33004030001P1] PPGQUIMICA-AP duplicata EXCLUIDO")
    
    db.session.commit()
    
    # BLOCO 6: Aceitar PPGTA multicampi (apenas documentar, não alterar)
    print("\n6. VERIFICANDO PPGTA MULTICAMPI")
    print("-" * 80)
    
    ppgta = ProgramaAcademico.query.filter_by(codigo_programa='40006018016P9').first()
    if ppgta:
        campus_atual = ppgta.campus.sigla_campus if ppgta.campus else "N/I"
        print(f"  [40006018016P9] Campus: {campus_atual}")
        print(f"  NOTA: Programa multicampi MD/CM - Campus principal e MD")
        print(f"  Bolsistas devem ser cadastrados no campus especifico (MD ou CM)")
    
    print("\n" + "=" * 80)
    print("CORRECOES APLICADAS COM SUCESSO!")
    print("=" * 80)
