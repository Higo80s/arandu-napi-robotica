"""
BACKUP PREVENTIVO - SNAPSHOT ANTES DA FASE 2
==============================================
Data: 29/01/2026 18:01
Motivo: Segurança antes de implementar Sistema de Backup Automático

Este script cria um backup manual do PostgreSQL local.
"""

import subprocess
import os
from datetime import datetime

# Configurações
DB_NAME = 'gestao_editais'
DB_USER = 'postgres'
DB_PASSWORD = 'admin123'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Diretório de backup
BACKUP_DIR = 'backups/postgres/manual'
os.makedirs(BACKUP_DIR, exist_ok=True)

# Nome do arquivo
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(BACKUP_DIR, f'SNAPSHOT_FASE2_INICIO_{timestamp}.sql')

print("=" * 80)
print("🔒 BACKUP PREVENTIVO - SNAPSHOT DO SISTEMA")
print("=" * 80)
print(f"Banco: {DB_NAME}")
print(f"Destino: {backup_file}")
print()

# Comando pg_dump
# Nota: No Windows, pg_dump.exe está no diretório de instalação do PostgreSQL
pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"

# Verificar se pg_dump existe
if not os.path.exists(pg_dump_path):
    print("⚠️  ERRO: pg_dump.exe não encontrado.")
    print(f"   Procurado em: {pg_dump_path}")
    print()
    print("📍 INSTRUÇÕES:")
    print("   1. Localize onde o PostgreSQL foi instalado")
    print("   2. Normalmente está em: C:\\Program Files\\PostgreSQL\\[versão]\\bin\\")
    print("   3. Atualize a variável 'pg_dump_path' neste script")
    exit(1)

try:
    # Definir senha via variável de ambiente
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    # Executar pg_dump
    print("⏳ Executando backup...")
    result = subprocess.run(
        [
            pg_dump_path,
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-F', 'p',  # Format: plain SQL
            '-f', backup_file,
            DB_NAME
        ],
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Verificar tamanho do arquivo
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        print()
        print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
        print(f"📦 Arquivo: {backup_file}")
        print(f"📊 Tamanho: {size_mb:.2f} MB")
        print()
        print("🛡️  Sistema protegido. Fase 2 pode prosseguir com segurança.")
    else:
        print()
        print("❌ ERRO ao criar backup:")
        print(result.stderr)
        exit(1)
        
except Exception as e:
    print()
    print(f"❌ EXCEÇÃO: {e}")
    exit(1)

print("=" * 80)
