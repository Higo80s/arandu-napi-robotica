"""
Correção em massa de níveis dos programas
Baseado em códigos Sucupira e análise de nomes
"""

from app import app, db
from models import ProgramaAcademico

with app.app_context():
    print("=== CORRECAO EM MASSA DE NIVEIS ===\n")
    
    # Mapeamento de correções
    # Formato: {id: "niveis corretos"}
    correcoes = {
        # Apucarana
        1: "M,D",    # PPGEM-AP - Engenharia de Materiais
        29: "M,D",   # PPGEM - Engenharia de Materiais
        2: "M,D",    # PPGQUIMICA-AP
        30: "M,D",   # PPGQ - Química
        
        # Campo Mourão
        31: "M,D",   # PPGEA - Engenharia Aeroespacial
        3: "M,D",    # PPGAERO-CM
        4: "M,D",    # PPGIT-CM - Inovações Tecnológicas
        
        # Cornélio Procópio
        5: "M,D",    # PPGBIOINFO-CP - Bioinformática
        
        # Curitiba
        12: "M,D",   # PPGCA - Computação Aplicada
        38: "M,D",   # PPGCA - Computação Aplicada
        93: "M,D",   # PPGDP - Design Prospectivo
        33: "M,D",   # PPGEC - Engenharia Civil
        8: "M,D",    # PPGEE-CT - Engenharia Elétrica
        34: "M,D",   # PPGEE - Engenharia Elétrica
        10: "M,D",   # PPGEM-CT - Engenharia Mecânica
        9: "M,D",    # PPGFISICA-CT
        35: "M,D",   # PPGFA - Física
        36: "M,D",   # PPGMET - Metalurgia e Materiais
        11: "MP",    # PPGPGP - Planejamento e Governança (PROFISSIONAL)
        37: "MP",    # PPGPG - Planejamento e Governança (PROFISSIONAL)
        
        # Dois Vizinhos
        13: "M,D",   # PPGAA-DV - Agroecossistemas
        
        # Francisco Beltrão
        15: "M,D",   # PPGEA - Engenharia Ambiental
        
        # Guarapuava
        16: "M,D",   # PPGEM-GP - Engenharia Mecânica
        
        # Londrina
        19: "MP",    # PPGFLIGHT-LD - Engenharia de Voo (PROFISSIONAL)
        18: "MP",    # PPGEMAT - Ensino da Matemática (PROFISSIONAL)
        
        # Medianeira
        20: "M,D",   # PPGTC-MD - Tecnologias Computacionais
        
        # Multi
        75: "MP",    # PROFIAP - Administração Pública em Rede Nacional (PROFISSIONAL)
        
        # Pato Branco
        22: "M,D",   # PPGA - Agronomia
        21: "M,D",   # PPGEC - Engenharia Civil
        23: "M,D",   # PPGEE-PB - Engenharia Elétrica
        39: "M,D",   # PPGEE - Engenharia Elétrica
        24: "M,D",   # PPGLETRAS-PB - Letras
        
        # Ponta Grossa
        97: "M",     # EEO - Engenharia Eletrônica (Graduação - IC)
        63: "M,D",   # PPGEE - Engenharia Elétrica
        96: "M",     # EEL(grad) - Graduação - IC
        25: "M,D",   # PPGEP - Engenharia de Produção
        41: "M,D",   # PPGEP - Engenharia de Produção
        
        # Santa Helena
        27: "M,D",   # PPGRN-SH - Recursos Naturais
        
        # Toledo
        94: "M",     # CC-TD(grad) - Graduação - IC
        98: "M",     # EEO(grad) - Graduação - IC
        95: "M",     # EE - Graduação - IC
    }
    
    print(f"Total de correções: {len(correcoes)}\n")
    
    corrigidos = []
    erros = []
    
    for prog_id, niveis_correto in correcoes.items():
        prog = ProgramaAcademico.query.get(prog_id)
        
        if prog:
            niveis_antigo = prog.niveis
            prog.niveis = niveis_correto
            
            print(f"ID {prog_id:3d}: {prog.sigla_programa:15s} | {prog.nome_programa:45s}")
            print(f"       {niveis_antigo or 'None':10s} → {niveis_correto}")
            
            corrigidos.append(prog_id)
        else:
            print(f"❌ ID {prog_id} NÃO ENCONTRADO!")
            erros.append(prog_id)
    
    if not erros:
        db.session.commit()
        print(f"\n✅ {len(corrigidos)} programas corrigidos com sucesso!")
    else:
        print(f"\n⚠️  {len(erros)} erros encontrados. Rollback executado.")
        db.session.rollback()
    
    # Verificar resultado
    print("\n=== VERIFICAÇÃO FINAL ===")
    programas_ainda_sem = ProgramaAcademico.query.filter(
        (ProgramaAcademico.niveis == None) | 
        (ProgramaAcademico.niveis == '') |
        (ProgramaAcademico.niveis == 'None')
    ).count()
    
    print(f"Programas ainda sem níveis: {programas_ainda_sem}")
