"""
BLOCO 1: Revisão e Padronização de Cursos de Graduação
Criar modelo de catalogação padronizado para cursos de graduação
"""

from app import app, db
from models import ProgramaAcademico, Campus

# Mapeamento de cursos de graduação encontrados
CURSOS_GRADUACAO = [
    {"codigo_antigo": "CC-TD(grad)", "nome": "Ciência da Computação", "sigla": "CC-GRAD", "campus": "TD", "nivel": "Graduação"},
    {"codigo_antigo": "00", "nome": "Engenharia Eletrônica", "sigla": "ELEO-GRAD", "campus": "TD", "nivel": "Graduação"},
    {"codigo_antigo": "EEL(grad)", "nome": "Engenharia Elétrica", "sigla": "EEL-GRAD", "campus": "PG", "nivel": "Graduação"},
    {"codigo_antigo": "0000", "nome": "Engenharia Eletrônica", "sigla": "ELEO-GRAD", "campus": "PG", "nivel": "Graduação"},
    {"codigo_antigo": "EEO(grad)", "nome": "Engenharia Eletrônica", "sigla": "ELEO-GRAD", "campus": "TD", "nivel": "Graduação"},
]

# Padrão de códigos para graduação: GRAD-SIGLA-CAMPUS
# Exemplo: GRAD-CC-TD, GRAD-ELEO-PG

with app.app_context():
    print("=" * 80)
    print("BLOCO 1: PADRONIZAÇÃO DE CURSOS DE GRADUAÇÃO")
    print("=" * 80)
    
    campus_dict = {c.sigla_campus: c for c in Campus.query.all()}
    
    for idx, curso in enumerate(CURSOS_GRADUACAO, 1):
        # Buscar pelo código antigo
        prog = ProgramaAcademico.query.filter_by(codigo_programa=curso['codigo_antigo']).first()
        
        if prog:
            # Gerar novo código padronizado
            novo_codigo = f"GRAD-{curso['sigla'].replace('-GRAD', '')}-{curso['campus']}"
            
            print(f"\n{idx}. Encontrado: {curso['codigo_antigo']}")
            print(f"   Nome atual: {prog.nome_programa}")
            print(f"   Proposta:")
            print(f"     Código: {curso['codigo_antigo']} → {novo_codigo}")
            print(f"     Nome: {prog.nome_programa} → {curso['nome']} (Graduação)")
            print(f"     Sigla: {prog.sigla_programa} → {curso['sigla']}")
            print(f"     Campus: {prog.campus.sigla_campus if prog.campus else 'N/I'} → {curso['campus']}")
            print(f"     Nível: {prog.niveis or 'N/I'} → GRAD")
            
            # APLICAR CORREÇÃO (descomente para executar)
            # prog.codigo_programa = novo_codigo
            # prog.nome_programa = f"{curso['nome']} (Graduação)"
            # prog.sigla_programa = curso['sigla']
            # prog.campus_id = campus_dict[curso['campus']].id
            # prog.niveis = "GRAD"
            # prog.nota_capes = None  # Graduação não tem nota CAPES
            # db.session.commit()
            # print("   ✅ ATUALIZADO")
        else:
            print(f"\n{idx}. NÃO ENCONTRADO: {curso['codigo_antigo']}")
    
    print("\n" + "=" * 80)
    print("MODELO DE CATALOGAÇÃO PARA GRADUAÇÃO:")
    print("=" * 80)
    print("Código: GRAD-[SIGLA_CURSO]-[CAMPUS]")
    print("Nome: [Nome do Curso] (Graduação)")
    print("Sigla: [SIGLA]-GRAD")
    print("Níveis: GRAD")
    print("Nota CAPES: NULL (não aplicável)")
    print("=" * 80)

if __name__ == "__main__":
    pass
