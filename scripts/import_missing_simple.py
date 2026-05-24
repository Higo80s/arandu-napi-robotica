"""
Importar dados de programas faltantes - versao simplificada
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import ProgramaAcademico, BolsaVolumetriaAnual, AgenciaFomento
import pandas as pd
from datetime import datetime

# Ler planilhas oficiais
df_oficial = pd.read_csv('dados_planilhas_oficiais.csv', encoding='utf-8-sig')

# Mapeamento de agências
AGENCIA_MAP = {
    'capes_ppg': 'CAPES PPG',
    'capes_ies_proppg': 'CAPES IES PROPPG',
    'CNPq': 'CNPq',
    'CNPQ': 'CNPq',
    'Recursos, Propríós, Fundação Araucária': 'UTFPR',
    'Recursos Próprios, Fundação Araucária': 'UTFPR',
    'Outras': 'UTFPR',
    'UTFPR': 'UTFPR',
    'Fundação Araucária': 'UTFPR'
}

with open('import_missing_log.txt', 'w', encoding='utf-8') as log:
    log.write("IMPORTACAO DE PROGRAMAS FALTANTES\n")
    log.write("="*80 + "\n\n")
    
    with app.app_context():
        # 1. Identificar programas sem dados
        todos_programas = ProgramaAcademico.query.all()
        
        programas_com_bolsas = db.session.query(
            BolsaVolumetriaAnual.programa_id
        ).distinct().all()
        ids_com_bolsas = set([p[0] for p in programas_com_bolsas])
        
        programas_sem_dados = [p for p in todos_programas if p.id not in ids_com_bolsas]
        
        log.write(f"Programas sem dados: {len(programas_sem_dados)}\n\n")
        
        # 2. Verificar quais estão nas planilhas oficiais
        codigos_planilhas = set(df_oficial['codigo'].unique())
        
        programas_para_importar = []
        for prog in programas_sem_dados:
            if prog.codigo_programa in codigos_planilhas:
                programas_para_importar.append(prog)
                log.write(f"OK {prog.codigo_programa} - {prog.nome_programa}\n")
            else:
                log.write(f"SKIP {prog.codigo_programa} - {prog.nome_programa}\n")
        
        log.write(f"\nTotal a importar: {len(programas_para_importar)}\n\n")
        
        if len(programas_para_importar) == 0:
            log.write("Nenhum programa para importar!\n")
            print("Nenhum programa para importar!")
            exit(0)
        
        # 3. Buscar agências
        agencias = {ag.sigla: ag for ag in AgenciaFomento.query.all()}
        
        # 4. Importar dados
        total_inserido = 0
        
        for prog in programas_para_importar:
            codigo = prog.codigo_programa
            
            # Filtrar dados deste programa
            dados_prog = df_oficial[df_oficial['codigo'] == codigo].copy()
            
            # Mapear agências
            dados_prog['agencia_banco'] = dados_prog['agencia_original'].map(AGENCIA_MAP)
            dados_prog = dados_prog[dados_prog['agencia_banco'].notna()]
            
            log.write(f"\nImportando {codigo}: {len(dados_prog)} registros\n")
            
            for _, row in dados_prog.iterrows():
                ano = int(row['ano'])
                agencia_sigla = row['agencia_banco']
                nivel = row['nivel']
                qtd = int(row['quantidade'])
                
                if agencia_sigla not in agencias:
                    log.write(f"  Aviso: Agencia {agencia_sigla} nao encontrada!\n")
                    continue
                
                agencia = agencias[agencia_sigla]
                
                # Criar registro
                bolsa = BolsaVolumetriaAnual(
                    programa_id=prog.id,
                    ano_referencia=ano,
                    agencia_id=agencia.id,
                    nivel=nivel,
                    qtd_sistema=qtd,
                    justificativa_ajuste=f"Importado automaticamente em {datetime.now().strftime('%Y-%m-%d')}"
                )
                db.session.add(bolsa)
                total_inserido += 1
        
        # Commit
        db.session.commit()
        
        log.write("\n" + "="*80 + "\n")
        log.write("CONCLUIDO!\n")
        log.write(f"Programas importados: {len(programas_para_importar)}\n")
        log.write(f"Registros inseridos: {total_inserido}\n")
        
        print(f"SUCESSO: {len(programas_para_importar)} programas, {total_inserido} registros")

print("Log salvo em: import_missing_log.txt")
