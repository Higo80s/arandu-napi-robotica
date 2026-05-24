"""
Inserir dados de bolsas para os 3 programas conforme dados corretos fornecidos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, AgenciaFomento, BolsaVolumetriaAnual
from datetime import datetime

# Dados de bolsas conforme fornecido pelo usuário
ANOS = list(range(2014, 2026))  # 2014 a 2025

BOLSAS_DATA = {
    '40006018014P6': {
        'Mestrado': {
            'CAPES PPG': [0, 0, 0, 0, 0, 0, 0, 0, 17, 17, 9, 17],
            'CAPES IES PROPPG': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            'CNPq': [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 3],
            'UTFPR': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1]
        },
        'Doutorado': {
            'CAPES PPG': [17, 17, 17, 17, 16, 16, 15, 8, 18, 17, 6, 17],
            'CNPq': [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            'UTFPR': [2, 4, 0, 2, 2, 2, 6, 5, 2, 0, 0, 2]
        }
    },
    '40006018029P3': {
        'Mestrado': {
            'CAPES PPG': [4, 5, 5, 6, 4, 2, 3, 4, 0, 0, 6, 6],
            'CAPES IES PROPPG': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'UTFPR': [4, 2, 0, 3, 0, 5, 4, 3, 0, 0, 4, 3]
        }
    },
    '40006018185P5': {
        'Mestrado': {
            'CAPES PPG': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'CAPES IES PROPPG': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            'CNPq': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'UTFPR': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        }
    }
}

print("="*80)
print("INSERINDO BOLSAS NOS 3 PROGRAMAS")
print("="*80)
print()

with app.app_context():
    try:
        # Buscar agências e programas
        agencias = {ag.sigla: ag for ag in AgenciaFomento.query.all()}
        programas = {p.codigo_programa: p for p in ProgramaAcademico.query.all()}
        
        total_criados = 0
        total_atualizados = 0
        
        for codigo, dados_prog in BOLSAS_DATA.items():
            if codigo not in programas:
                print(f"⚠️  Programa {codigo} não encontrado no banco!")
                continue
            
            programa = programas[codigo]
            print(f"Processando: {codigo} - {programa.nome_programa}")
            
            for nivel, dados_nivel in dados_prog.items():
                for agencia_sigla, quantidades in dados_nivel.items():
                    if agencia_sigla not in agencias:
                        print(f"  ⚠️  Agência {agencia_sigla} não encontrada!")
                        continue
                    
                    agencia = agencias[agencia_sigla]
                    
                    for i, ano in enumerate(ANOS):
                        qtd = quantidades[i]
                        
                        # Ver if já existe
                        existe = BolsaVolumetriaAnual.query.filter_by(
                            programa_id=programa.id,
                            ano_referencia=ano,
                            agencia_id=agencia.id,
                            nivel=nivel
                        ).first()
                        
                        if existe:
                            # Atualizar se diferente
                            if existe.qtd_sistema != qtd:
                                existe.qtd_sistema = qtd
                                existe.justificativa_ajuste = f"Corrigido em {datetime.now().strftime('%Y-%m-%d')}"
                                total_atualizados += 1
                        else:
                            # Criar novo (criar todos, mesmo com qtd=0)
                            bolsa = BolsaVolumetriaAnual(
                                programa_id=programa.id,
                                ano_referencia=ano,
                                agencia_id=agencia.id,
                                nivel=nivel,
                                qtd_sistema=qtd,
                                justificativa_ajuste=f"Inserido em {datetime.now().strftime('%Y-%m-%d')}"
                            )
                            db.session.add(bolsa)
                            total_criados += 1
                    
                    # Resumo
                    total_ag = sum(quantidades)
                    if total_ag > 0:
                        print(f"  {nivel} | {agencia_sigla}: {total_ag} bolsas")
            
            print()
        
        # Commit
        db.session.commit()
        
        print("="*80)
        print("✅ CONCLUÍDO COM SUCESSO!")
        print("="*80)
        print(f"Registros criados: {total_criados}")
        print(f"Registros atualizados: {total_atualizados}")
        print()
        print("Verifique o relatório de evolução:")
        print("  http://127.0.0.1:5003/reports/evolution/view")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        raise
