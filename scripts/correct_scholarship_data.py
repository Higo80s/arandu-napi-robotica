"""
Corrigir dados de bolsas para os 3 programas com valores CORRETOS
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, AgenciaFomento, BolsaVolumetriaAnual
from datetime import datetime

# DADOS CORRETOS conforme fornecido pelo usuário
ANOS = list(range(2014, 2026))

BOLSAS_CORRETAS = {
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
print("CORRIGINDO DADOS DE BOLSAS - 3 PROGRAMAS")
print("="*80)
print()

with app.app_context():
    try:
        # Buscar agências e programas
        agencias = {ag.sigla: ag for ag in AgenciaFomento.query.all()}
        programas = {p.codigo_programa: p for p in ProgramaAcademico.query.all()}
        
        total_deletados = 0
        total_inseridos = 0
        
        for codigo in BOLSAS_CORRETAS.keys():
            if codigo not in programas:
                print(f"ERRO: Programa {codigo} não encontrado!")
                continue
            
            programa = programas[codigo]
            print(f"1. Processando {codigo} - {programa.nome_programa}")
            
            # DELETAR dados existentes deste programa
            deletados = BolsaVolumetriaAnual.query.filter_by(programa_id=programa.id).delete()
            total_deletados += deletados
            print(f"   Deletados: {deletados} registros existentes")
            
            # INSERIR dados corretos
            dados_prog = BOLSAS_CORRETAS[codigo]
            
            for nivel, dados_nivel in dados_prog.items():
                for agencia_sigla, quantidades in dados_nivel.items():
                    if agencia_sigla not in agencias:
                        print(f"   ERRO: Agência {agencia_sigla} não encontrada!")
                        continue
                    
                    agencia = agencias[agencia_sigla]
                    
                    # Inserir para cada ano
                    for i, ano in enumerate(ANOS):
                        qtd = quantidades[i]
                        
                        bolsa = BolsaVolumetriaAnual(
                            programa_id=programa.id,
                            ano_referencia=ano,
                            agencia_id=agencia.id,
                            nivel=nivel,
                            qtd_sistema=qtd,
                            justificativa_ajuste=f"Correcao manual {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        )
                        db.session.add(bolsa)
                        total_inseridos += 1
                    
                    # Resumo
                    total_ag = sum(quantidades)
                    if total_ag > 0:
                        print(f"   + {nivel} | {agencia_sigla}: {total_ag} bolsas")
            
            print()
        
        # Commit
        db.session.commit()
        
        print("="*80)
        print("CONCLUIDO COM SUCESSO!")
        print("="*80)
        print(f"Total deletado: {total_deletados}")
        print(f"Total inserido: {total_inseridos}")
        print()
        print("Verifique: http://127.0.0.1:5003/reports/evolution/view")
        
    except Exception as e:
        db.session.rollback()
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        raise
