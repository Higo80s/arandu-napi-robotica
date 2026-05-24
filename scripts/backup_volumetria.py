"""
Script para fazer backup completo da tabela BolsaVolumetriaAnual
EXECUTAR ANTES de qualquer atualização!
"""
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BolsaVolumetriaAnual, ProgramaAcademico, AgenciaFomento
import pandas as pd

OUTPUT_DIR = 'backups'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# Criar diretório de backup se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("BACKUP DA TABELA BolsaVolumetriaAnual")
print("="*80)
print(f"Timestamp: {TIMESTAMP}")
print()

with app.app_context():
    # Contar registros
    total = BolsaVolumetriaAnual.query.count()
    print(f"Total de registros a fazer backup: {total}")
    
    # Buscar todos os registros
    registros = BolsaVolumetriaAnual.query.all()
    
    # Preparar dados para CSV
    dados = []
    for vol in registros:
        dados.append({
            'id': vol.id,
            'programa_id': vol.programa_id,
            'ano_referencia': vol.ano_referencia,
            'agencia_id': vol.agencia_id,
            'nivel': vol.nivel,
            'qtd_sistema': vol.qtd_sistema,
            'qtd_manual_extra': vol.qtd_manual_extra or 0,
            'justificativa_ajuste': vol.justificativa_ajuste,
            'updated_by_user_id': vol.updated_by_user_id,
            # Campos adicionais para restauração completa
            'programa_codigo': vol.programa.codigo_programa if vol.programa else None,
            'agencia_sigla': vol.agencia.sigla if vol.agencia else None
        })
    
    # Salvar CSV
    df = pd.DataFrame(dados)
    csv_file = os.path.join(OUTPUT_DIR, f'volumetria_backup_{TIMESTAMP}.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✓ Backup CSV salvo: {csv_file}")
    
    # Criar SQL de restauração
    sql_file = os.path.join(OUTPUT_DIR, f'volumetria_restore_{TIMESTAMP}.sql')
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(f"-- BACKUP DA TABELA bolsa_volumetria_anual\n")
        f.write(f"-- Criado em: {datetime.now()}\n")
        f.write(f"-- Total de registros: {total}\n\n")
        
        f.write("-- Para restaurar, execute:\n")
        f.write("-- 1. DELETE FROM bolsa_volumetria_anual;\n")
        f.write("-- 2. Execute os INSERTs abaixo\n\n")
        
        f.write("BEGIN;\n\n")
        
        for vol in registros:
            qtd_manual = vol.qtd_manual_extra or 0
            justificativa = vol.justificativa_ajuste or ''
            justificativa_escaped = justificativa.replace("'", "''")
            
            sql = f"""INSERT INTO bolsa_volumetria_anual 
    (id, programa_id, ano_referencia, agencia_id, nivel, qtd_sistema, qtd_manual_extra, justificativa_ajuste, updated_by_user_id)
VALUES 
    ({vol.id}, {vol.programa_id}, {vol.ano_referencia}, {vol.agencia_id}, '{vol.nivel}', {vol.qtd_sistema}, {qtd_manual}, '{justificativa_escaped}', {vol.updated_by_user_id or 'NULL'});\n"""
            f.write(sql)
        
        f.write("\nCOMMIT;\n")
    
    print(f"✓ SQL de restauração salvo: {sql_file}")
    
    # Estatísticas do backup
    print(f"\nEstatísticas do backup:")
    print(f"  Total de registros: {len(dados)}")
    print(f"  Anos: {sorted(df['ano_referencia'].unique())}")
    print(f"  Níveis: {df['nivel'].unique()}")
    print(f"  Agências: {df['agencia_sigla'].value_counts().to_dict()}")
    
    # Criar arquivo de instruções
    readme_file = os.path.join(OUTPUT_DIR, f'RESTORE_INSTRUCTIONS_{TIMESTAMP}.txt')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(f"INSTRUÇÕES PARA RESTAURAR BACKUP\n")
        f.write(f"="*80 + "\n\n")
        f.write(f"Data do backup: {datetime.now()}\n")
        f.write(f"Total de registros: {total}\n\n")
        
        f.write(f"OPÇÃO 1 - Restaurar via CSV:\n")
        f.write(f"-" * 80 + "\n")
        f.write(f"1. Abra o arquivo: {csv_file}\n")
        f.write(f"2. Use uma ferramenta de importação CSV para PostgreSQL\n")
        f.write(f"3. Mapeie as colunas corretamente\n\n")
        
        f.write(f"OPÇÃO 2 - Restaurar via SQL:\n")
        f.write(f"-" * 80 + "\n")
        f.write(f"1. Conecte ao banco PostgreSQL\n")
        f.write(f"2. Execute: DELETE FROM bolsa_volumetria_anual;\n")
        f.write(f"3. Execute o arquivo: {sql_file}\n\n")
        
        f.write(f"OPÇÃO 3 - Restaurar via Python:\n")
        f.write(f"-" * 80 + "\n")
        f.write(f"Execute: python scripts/restore_volumetria.py {csv_file}\n\n")
    
    print(f"✓ Instruções de restauração: {readme_file}")

print()
print("="*80)
print("BACKUP CONCLUÍDO COM SUCESSO!")
print("="*80)
print()
print("IMPORTANTE:")
print("  - Guarde os arquivos de backup em local seguro")
print("  - Não delete os arquivos até confirmar que a atualização funcionou")
print("  - Use as instruções para restaurar caso necessário")
print()
