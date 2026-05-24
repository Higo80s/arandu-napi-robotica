"""
BLOCO 2: Correções Específicas Conforme Sucupira
"""

from app import app, db
from models import ProgramaAcademico, Campus

CORRECOES = {
    # Design Prospectivo - MANTER (está correto)
    "40006018184P9": {
        "acao": "MANTER",
        "motivo": "Programa novo 2025, dados corretos"
    },
    
    # Educação Tecnológica - MANTER (está correto)
    "40006018185P5": {
        "acao": "MANTER",
        "motivo": "Programa novo 2025, dados corretos"
    },
    
    # PPGECT - SEPARAR mestrado e doutorado
    "40006018028P7": {
        "acao": "ATUALIZAR",
        "campo": "nome_programa",
        "antigo": "ENSINO DE CIENCIA E TECNOLOGIA (DOUTORADO)",
        "novo": "ENSINO DE CIÊNCIA E TECNOLOGIA",
        "niveis": "D",
        "motivo": "Doutorado do PPGECT - separado do mestrado"
    },
    
    "40006018006P3": {
        "acao": "VERIFICAR_EXISTENCIA",
        "nome": "ENSINO DE CIÊNCIA E TECNOLOGIA",
        "sigla": "PPGECT",
        "campus": "PG",
        "niveis": "MP",
        "nota": "5",
        "ano": 2008,
        "motivo": "Mestrado Profissional do PPGECT"
    },
    
    # Duplicatas para EXCLUIR
    "33004010001P1": {
        "acao": "EXCLUIR",
        "motivo": "Duplicata - Engenharia de Materiais AP já existe como PPGEM-AP"
    },
    
    "33004030001P1": {
        "acao": "EXCLUIR",
        "motivo": "Duplicata - Química AP já existe"
    },
    
    # PPGTA - Aceitar multicampi
    "40006018016P9": {
        "acao": "ACEITAR_MULTICAMPI",
        "campus_texto": "MD/CM",
        "campus_principal": "MD",
        "motivo": "Programa multicampi Medianeira/Campo Mourão"
    },
    
    # PPGIT - Corrigir níveis
    "40006018170P8": {
        "acao": "ATUALIZAR",
        "campo": "niveis",
        "antigo": "M,MP",
        "novo": "MP",
        "motivo": "É Mestrado Profissional, não precisa duplicar com M"
    }
}

with app.app_context():
    print("=" * 80)
    print("BLOCO 2: CORREÇÕES ESPECÍFICAS")
    print("=" * 80)
    
    for codigo, acao_dict in CORRECOES.items():
        prog = ProgramaAcademico.query.filter_by(codigo_programa=codigo).first()
        
        print(f"\nCódigo: {codigo}")
        print(f"Ação: {acao_dict['acao']}")
        
        if acao_dict['acao'] == "MANTER":
            if prog:
                print(f"  ✅ Encontrado: {prog.nome_programa} - {prog.sigla_programa}")
                print(f"  📌 {acao_dict['motivo']}")
            else:
                print(f"  ⚠️  NÃO ENCONTRADO no banco")
        
        elif acao_dict['acao'] == "ATUALIZAR":
            if prog:
                campo = acao_dict['campo']
                valor_atual = getattr(prog, campo)
                print(f"  Encontrado: {prog.nome_programa}")
                print(f"  Campo '{campo}':")
                print(f"    Atual: {valor_atual}")
                print(f"    Novo: {acao_dict['novo']}")
                print(f"  📌 {acao_dict['motivo']}")
                
                # APLICAR (descomente para executar)
                # setattr(prog, campo, acao_dict['novo'])
                # db.session.commit()
                # print("  ✅ ATUALIZADO")
            else:
                print(f"  ⚠️  NÃO ENCONTRADO")
        
        elif acao_dict['acao'] == "EXCLUIR":
            if prog:
                print(f"  ❌ Para excluir: {prog.nome_programa} - {prog.sigla_programa}")
                print(f"  📌 {acao_dict['motivo']}")
                
                # EXCLUIR (descomente para executar)
                # db.session.delete(prog)
                # db.session.commit()
                # print("  ✅ EXCLUÍDO")
            else:
                print(f"  ✅ Já não existe no banco")
        
        elif acao_dict['acao'] == "VERIFICAR_EXISTENCIA":
            if prog:
                print(f"  ✅ Já existe: {prog.nome_programa}")
                print(f"  Níveis: {prog.niveis}")
            else:
                print(f"  ⚠️  NÃO ENCONTRADO - precisa criar")
                print(f"  Nome: {acao_dict['nome']}")
                print(f"  Sigla: {acao_dict['sigla']}")
                print(f"  Campus: {acao_dict['campus']}")
                print(f"  Níveis: {acao_dict['niveis']}")
        
        elif acao_dict['acao'] == "ACEITAR_MULTICAMPI":
            if prog:
                print(f"  ✅ Programa multicampi: {prog.nome_programa}")
                print(f"  Campus atual no banco: {prog.campus.sigla_campus if prog.campus else 'N/I'}")
                print(f"  Campus correto (Sucupira): {acao_dict['campus_texto']}")
                print(f"  Campus principal: {acao_dict['campus_principal']}")
                print(f"  📌 {acao_dict['motivo']}")
                print(f"  💡 NOTA: Bolsistas devem ser vinculados ao campus principal específico")
            else:
                print(f"  ⚠️  NÃO ENCONTRADO")
    
    print("\n" + "=" * 80)
    print("RESUMO DE AÇÕES:")
    print("=" * 80)
    manter = sum(1 for a in CORRECOES.values() if a['acao'] == 'MANTER')
    atualizar = sum(1 for a in CORRECOES.values() if a['acao'] == 'ATUALIZAR')
    excluir = sum(1 for a in CORRECOES.values() if a['acao'] == 'EXCLUIR')
    verificar = sum(1 for a in CORRECOES.values() if a['acao'] == 'VERIFICAR_EXISTENCIA')
    multicampi = sum(1 for a in CORRECOES.values() if a['acao'] == 'ACEITAR_MULTICAMPI')
    
    print(f"  Manter: {manter}")
    print(f"  Atualizar: {atualizar}")
    print(f"  Excluir: {excluir}")
    print(f"  Verificar existência: {verificar}")
    print(f"  Aceitar multicampi: {multicampi}")
    print("=" * 80)

if __name__ == "__main__":
    pass
