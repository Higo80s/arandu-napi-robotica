"""
Script para cadastrar programas de mestrado faltantes com dados completos
Fonte: Plataforma Sucupira 2025
"""

from app import app, db
from models import ProgramaAcademico, Campus
from sqlalchemy import text

# Mapeamento de siglas de campus para IDs
campus_map = {
    'CT': None, 'DV': None, 'SH': None, 'CP': None, 'PG': None,
    'CM': None, 'LD': None, 'AP': None, 'FB': None, 'PB': None
}

# Dados completos dos 11 programas
programas = [
    {
        'codigo': '40006018044P2',
        'nome': 'ADMINISTRAÇÃO',
        'sigla': 'PPGA',
        'campus': 'CT',
        'niveis': 'M',
        'area_avaliacao': 'ADMINISTRAÇÃO PÚBLICA E DE EMPRESAS, CIÊNCIAS CONTÁBEIS E TURISMO',
        'area_basica': 'ADMINISTRAÇÃO',
        'ano_inicio': 2016,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018043P6',
        'nome': 'AGROECOSSISTEMAS',
        'sigla': 'PPGSIS',
        'campus': 'DV',  # DV/SH - usar DV
        'niveis': 'M',
        'area_avaliacao': 'CIÊNCIAS AGRÁRIAS I',
        'area_basica': 'AGRONOMIA',
        'ano_inicio': 2015,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018037P6',
        'nome': 'BIOINFORMÁTICA',
        'sigla': 'PPGBIOINFO',
        'campus': 'CP',
        'niveis': 'M',
        'area_avaliacao': 'CIÊNCIAS BIOLÓGICAS I',
        'area_basica': 'GENÉTICA',
        'ano_inicio': 2015,
        'nota_capes': '4'
    },
    {
        'codigo': '40006018171P4',
        'nome': 'CIÊNCIA DA COMPUTAÇÃO',
        'sigla': 'PPGCC',
        'campus': 'PG',
        'niveis': 'M',
        'area_avaliacao': 'CIÊNCIA DA COMPUTAÇÃO',
        'area_basica': 'CIÊNCIA DA COMPUTAÇÃO',
        'ano_inicio': 2016,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018182P6',
        'nome': 'Ciência da Computação',
        'sigla': 'PPGCC',
        'campus': 'CM',
        'niveis': 'M',
        'area_avaliacao': 'CIÊNCIA DA COMPUTAÇÃO',
        'area_basica': 'CIÊNCIA DA COMPUTAÇÃO',
        'ano_inicio': 2021,
        'nota_capes': 'A'
    },
    {
        'codigo': '40006018175P0',
        'nome': 'CIÊNCIA E ENGENHARIA DE MATERIAIS',
        'sigla': 'PPGCEM',
        'campus': 'LD',  # LD/AP - usar LD
        'niveis': 'M',
        'area_avaliacao': 'MATERIAIS',
        'area_basica': 'MATERIAIS',
        'ano_inicio': 2016,
        'nota_capes': '4'
    },
    {
        'codigo': '40006018173P7',
        'nome': 'Educação Física',
        'sigla': 'PPGEF',
        'campus': 'CT',
        'niveis': 'M',
        'area_avaliacao': 'EDUCAÇÃO FÍSICA',
        'area_basica': 'EDUCAÇÃO FÍSICA',
        'ano_inicio': 2017,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018023P5',
        'nome': 'Engenharia Ambiental',
        'sigla': 'PPGEA',
        'campus': 'LD',  # LD/AP - usar LD
        'niveis': 'M',
        'area_avaliacao': 'ENGENHARIAS I',
        'area_basica': 'ENGENHARIA SANITÁRIA',
        'ano_inicio': 2012,
        'nota_capes': '4'
    },
    {
        'codigo': '40006018174P3',
        'nome': 'Engenharia Ambiental: Análise e Tecnologia Ambiental',
        'sigla': 'PPGEA',
        'campus': 'FB',
        'niveis': 'M',
        'area_avaliacao': 'ENGENHARIAS I',
        'area_basica': 'ENGENHARIA SANITÁRIA',
        'ano_inicio': 2017,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018030P1',
        'nome': 'Engenharia Civil',
        'sigla': 'PPGEC',
        'campus': 'PB',
        'niveis': 'M',
        'area_avaliacao': 'ENGENHARIAS I',
        'area_basica': 'ENGENHARIA CIVIL',
        'ano_inicio': 2014,
        'nota_capes': '3'
    },
    {
        'codigo': '40006018031P8',
        'nome': 'Engenharia de Produção e Sistemas',
        'sigla': 'PPGEPS',
        'campus': 'PB',
        'niveis': 'M',
        'area_avaliacao': 'ENGENHARIAS III',
        'area_basica': 'ENGENHARIA DE PRODUÇÃO',
        'ano_inicio': 2014,
        'nota_capes': '3'
    }
]


def cadastrar_programas():
    """Cadastra os 11 programas faltantes no banco de dados"""
    
    with app.app_context():
        print("=" * 70)
        print("CADASTRO DE PROGRAMAS DE MESTRADO FALTANTES")
        print("=" * 70)
        
        # 1. Buscar IDs dos campi
        print("\n1. Mapeando campi...")
        campi = Campus.query.all()
        for c in campi:
            if c.sigla_campus in campus_map:
                campus_map[c.sigla_campus] = c.id
                print(f"   {c.sigla_campus} → ID {c.id} ({c.nome})")
        
        # 2. Processar cada programa
        print("\n2. Cadastrando programas...")
        cadastrados = 0
        atualizados = 0
        erros = []
        
        for prog_data in programas:
            codigo = prog_data['codigo']
            campus_sigla = prog_data['campus']
            
            # Verificar se campus existe
            campus_id = campus_map.get(campus_sigla)
            if not campus_id:
                erros.append(f"{codigo}: Campus '{campus_sigla}' não encontrado")
                continue
            
            # Verificar se programa já existe (por código)
            prog_existente = ProgramaAcademico.query.filter_by(codigo_programa=codigo).first()
            
            if prog_existente:
                # Atualizar dados
                prog_existente.nome_programa = prog_data['nome']
                prog_existente.sigla_programa = prog_data['sigla']
                prog_existente.campus_id = campus_id
                prog_existente.niveis = prog_data['niveis']
                prog_existente.area_avaliacao = prog_data['area_avaliacao']
                prog_existente.area_basica = prog_data['area_basica']
                prog_existente.ano_inicio = prog_data['ano_inicio']
                prog_existente.nota_capes = prog_data['nota_capes']
                
                print(f"   ✅ {prog_data['sigla']} ({campus_sigla}): ATUALIZADO")
                atualizados += 1
            else:
                # Cadastrar novo
                novo_prog = ProgramaAcademico(
                    codigo_programa=codigo,
                    nome_programa=prog_data['nome'],
                    sigla_programa=prog_data['sigla'],
                    campus_id=campus_id,
                    niveis=prog_data['niveis'],
                    area_avaliacao=prog_data['area_avaliacao'],
                    area_basica=prog_data['area_basica'],
                    ano_inicio=prog_data['ano_inicio'],
                    nota_capes=prog_data['nota_capes']
                )
                db.session.add(novo_prog)
                print(f"   ✅ {prog_data['sigla']} ({campus_sigla}): CADASTRADO")
                cadastrados += 1
        
        # Commit
        try:
            db.session.commit()
            print("\n✅ Commit realizado com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERRO no commit: {e}")
            return
        
        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO")
        print("=" * 70)
        print(f"Programas cadastrados: {cadastrados}")
        print(f"Programas atualizados: {atualizados}")
        if erros:
            print(f"\n⚠️ Erros ({len(erros)}):")
            for erro in erros:
                print(f"   - {erro}")
        print("=" * 70)
        print("\n✅ Processo concluído!")
        print("\nPróximo passo: Execute 'python atualizar_cotas_capes_mestrado.py'")


if __name__ == '__main__':
    cadastrar_programas()
