"""
Script para atualizar BolsaVolumetriaAnual com dados oficiais das planilhas PROPPG
IMPORTANTE: Backup foi criado antes da execução!
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BolsaVolumetriaAnual, ProgramaAcademico, AgenciaFomento
import pandas as pd
from datetime import datetime

# Arquivo com dados oficiais
DADOS_OFICIAIS = 'dados_planilhas_oficiais.csv'
LOG_FILE = f'update_volumetria_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# Mapeamento de agências (planilha -> banco)
AGENCIA_MAP = {
    'capes_ppg': 'CAPES PPG',
    'capes_ies_proppg': 'CAPES IES PROPPG',  # Manter separados!
    'CNPq': 'CNPq',
    'CNPQ': 'CNPq',
    'Recursos, Propríos, Fundação Araucária': 'UTFPR',
    'Recursos Próprios, Fundação Araucária': 'UTFPR',
    'Outras': 'UTFPR',
    'UTFPR': 'UTFPR',
    'Fundação Araucária': 'UTFPR'
}

class Logger:
    def __init__(self, filename):
        self.file = open(filename, 'w', encoding='utf-8')
    
    def log(self, msg):
        print(msg)
        self.file.write(msg + '\n')
        self.file.flush()
    
    def close(self):
        self.file.close()

logger = Logger(LOG_FILE)

logger.log("="*80)
logger.log("ATUALIZAÇÃO DE DADOS DE BOLSAS - DADOS OFICIAIS PROP PG")
logger.log("="*80)
logger.log(f"Inicio: {datetime.now()}")
logger.log("")

# Ler dados oficiais
logger.log(f"Lendo dados oficiais: {DADOS_OFICIAIS}")
df_oficiais = pd.read_csv(DADOS_OFICIAIS, encoding='utf-8-sig')
logger.log(f"Total de registros oficiais: {len(df_oficiais)}")
logger.log("")

# Estatísticas dos dados oficiais
logger.log("Distribuição por agência (oficial):")
for ag, count in df_oficiais['agencia_original'].value_counts().items():
    logger.log(f"  {ag}: {count}")
logger.log("")

with app.app_context():
    try:
        # Buscar IDs de agências
        logger.log("Mapeando agências para IDs do banco...")
        agencias = {ag.sigla: ag.id for ag in AgenciaFomento.query.all()}
        logger.log(f"Agências no banco: {list(agencias.keys())}")
        logger.log("")
        
        # Preparar agregação (SEM somar capes_ppg + capes_ies_proppg - manter separados!)
        logger.log("Processando dados oficiais (CAPES PPG e CAPES IES PROPPG serão mantidos SEPARADOS)...")
        
        # Adicionar coluna de agência mapeada
        df_oficiais['agencia_banco'] = df_oficiais['agencia_original'].map(AGENCIA_MAP)
        
        # Identificar NaN
        nans = df_oficiais[df_oficiais['agencia_banco'].isna()]
        if len(nans) > 0:
            logger.log(f"⚠️  AVISO: {len(nans)} registros com agência não mapeada:")
            for ag in nans['agencia_original'].unique():
                logger.log(f"    - {ag}")
            logger.log("")
        
        # Remover NaNs
        df_oficiais = df_oficiais[df_oficiais['agencia_banco'].notna()]
        
        # NÃO agregar! Manter capes_ppg e capes_ies_proppg separados
        df_agregado = df_oficiais[['codigo', 'ano', 'agencia_banco', 'nivel', 'quantidade']].copy()
        
        logger.log(f"Total de registros a processar: {len(df_agregado)}")
        logger.log("")
        
        # Estatísticas
        logger.log("Distribuição por agência (após agregação):")
        for ag, count in df_agregado['agencia_banco'].value_counts().items():
            logger.log(f"  {ag}: {count}")
        logger.log("")
        
        # Buscar programas e mapear código -> programa_id
        logger.log("Mapeando códigos de programa para IDs...")
        programas = {}
        for prog in ProgramaAcademico.query.all():
            codigo_limpo = prog.codigo_programa.strip().replace('\n', '').replace('"', '')
            programas[codigo_limpo] = prog.id
        
        logger.log(f"Total de programas mapeados: {len(programas)}")
        logger.log("")
        
        # Processar atualizações
        logger.log("="*80)
        logger.log("PROCESSANDO ATUALIZAÇÕES")
        logger.log("="*80)
        logger.log("")
        
        criados = 0
        atualizados = 0
        sem_mudanca = 0
        erros = 0
        nao_encontrados = []
        
        for idx, row in df_agregado.iterrows():
            codigo = row['codigo']
            ano = int(row['ano'])
            agencia_sigla = row['agencia_banco']
            nivel = row['nivel']
            qtd_oficial = int(row['quantidade'])
            
            # Verificar se programa existe
            if codigo not in programas:
                if codigo not in [n[0] for n in nao_encontrados]:
                    nao_encontrados.append((codigo, nivel))
                continue
            
            programa_id = programas[codigo]
            
            # Verificar se agência existe
            if agencia_sigla not in agencias:
                logger.log(f"  ERRO: Agência não encontrada: {agencia_sigla}")
                erros += 1
                continue
            
            agencia_id = agencias[agencia_sigla]
            
            # Buscar registro existente
            vol = BolsaVolumetriaAnual.query.filter_by(
                programa_id=programa_id,
                ano_referencia=ano,
                agencia_id=agencia_id,
                nivel=nivel
            ).first()
            
            if vol:
                # Atualizar se diferente
                if vol.qtd_sistema != qtd_oficial:
                    logger.log(f"  ATUALIZAR: {codigo} | {nivel} | {agencia_sigla} | {ano} | {vol.qtd_sistema} -> {qtd_oficial}")
                    vol.qtd_sistema = qtd_oficial
                    vol.justificativa_ajuste = f"Atualizado com dados oficiais PROPPG em {datetime.now().strftime('%Y-%m-%d')}"
                    atualizados += 1
                else:
                    sem_mudanca += 1
            else:
                # Criar novo
                logger.log(f"  CRIAR: {codigo} | {nivel} | {agencia_sigla} | {ano} | qtd={qtd_oficial}")
                vol = BolsaVolumetriaAnual(
                    programa_id=programa_id,
                    ano_referencia=ano,
                    agencia_id=agencia_id,
                    nivel=nivel,
                    qtd_sistema=qtd_oficial,
                    justificativa_ajuste=f"Criado com dados oficiais PROPPG em {datetime.now().strftime('%Y-%m-%d')}"
                )
                db.session.add(vol)
                criados += 1
            
            # Commit parcial a cada 100 registros
            if (criados + atualizados) % 100 == 0:
                db.session.commit()
                logger.log(f"  ... Checkpoint: {criados + atualizados} registros processados")
        
        # Commit final
        db.session.commit()
        
        logger.log("")
        logger.log("="*80)
        logger.log("RESUMO DAS ALTERAÇÕES")
        logger.log("="*80)
        logger.log(f"Registros criados: {criados}")
        logger.log(f"Registros atualizados: {atualizados}")
        logger.log(f"Registros sem mudança: {sem_mudanca}")
        logger.log(f"Erros: {erros}")
        
        if nao_encontrados:
            logger.log(f"\nProgramas não encontrados no banco ({len(nao_encontrados)}):")
            for codigo, nivel in nao_encontrados[:20]:  # Mostrar até 20
                logger.log(f"  - {codigo} ({nivel})")
            if len(nao_encontrados) > 20:
                logger.log(f"  ... e mais {len(nao_encontrados) - 20}")
        
        logger.log("")
        logger.log("="*80)
        logger.log("✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.log("="*80)
        logger.log(f"Fim: {datetime.now()}")
        logger.log("")
        logger.log("IMPORTANTE:")
        logger.log("  - Verifique o relatório de evolução em: http://127.0.0.1:5003/reports/evolution/view")
        logger.log("  - Se houver problemas, restaure o backup usando:")
        logger.log("    python scripts/restore_volumetria.py backups/volumetria_backup_XXXXXX.csv")
        logger.log("")
        
    except Exception as e:
        db.session.rollback()
        logger.log("")
        logger.log("="*80)
        logger.log("❌ ERRO DURANTE ATUALIZAÇÃO!")
        logger.log("="*80)
        logger.log(f"Erro: {e}")
        import traceback
        logger.log(traceback.format_exc())
        logger.log("")
        logger.log("A transação foi revertida (ROLLBACK).")
        logger.log("Nenhuma alteração foi salva no banco de dados.")
        logger.log("")
        raise

logger.close()
print(f"\nLog completo salvo em: {LOG_FILE}")
