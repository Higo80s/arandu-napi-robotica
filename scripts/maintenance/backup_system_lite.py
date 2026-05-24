"""
backup_system_lite.py - Versão rápida e leve do backup
=========================================================

PROBLEMA IDENTIFICADO:
- backup_system.py processa TODOS os arquivos do projeto
- Isso pode incluir milhares de arquivos (.venv backup, logs, etc)
- Demora muito tempo, causando timeout HTTP no navegador

SOLUÇÃO:
- Backup APENAS de arquivos essenciais:
  * models.py, app.py, utils/
  * templates/
  * static/ (apenas CSS e JS importantes)
  * Banco de dados PostgreSQL (via pg_dump)
  * Arquivo .env

- Processamento rápido: < 5 segundos
"""

import os
import zipfile
import datetime
import subprocess
import shutil
from urllib.parse import urlparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')

# APENAS arquivos e pastas ESSENCIAIS
ESSENTIAL_FILES = [
    'app.py',
    'models.py',
    'requirements.txt',
    '.env',
    'README.md'
]

ESSENTIAL_DIRS = [
    'templates',
    'static/css',
    'static/js',
    'static/images',
    'utils'
]

def backup_postgres_quick(db_url, output_path):
    """Backup rápido PostgreSQL com pg_dump"""
    try:
        parsed = urlparse(db_url)
        if not parsed.scheme or 'postgres' not in parsed.scheme:
            return None
        
        cmd = [
            'pg_dump',
            '-h', parsed.hostname or 'localhost',
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '-F', 'c',
            '-f', output_path
        ]
        
        env = os.environ.copy()
        if parsed.password:
            env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return output_path
        return None
    except:
        return None

def create_backup_lite(flask_app=None):
    """
    Cria backup RÁPIDO apenas com arquivos essenciais
    Tempo estimado: 2-5 segundos
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"gestao_editais_lite_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    print(f"\n{'='*50}")
    print(f"BACKUP LITE - Apenas Arquivos Essenciais")
    print(f"{'='*50}\n")

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # 1. BANCO DE DADOS (se PostgreSQL)
            db_url = os.getenv('DATABASE_URL')
            if db_url and 'postgres' in db_url:
                print("📊 Backup PostgreSQL...")
                pg_file = os.path.join(BACKUP_DIR, f"db_{timestamp}.dump")
                if backup_postgres_quick(db_url, pg_file):
                    zipf.write(pg_file, f"database/postgres.dump")
                    os.remove(pg_file)
                    print("   ✅ Banco incluído")
                else:
                    print("   ⚠️  pg_dump falhou (não crítico)")
            
            # 2. ARQUIVOS ESSENCIAIS
            print("\n📁 Arquivos essenciais...")
            for filename in ESSENTIAL_FILES:
                filepath = os.path.join(PROJECT_ROOT, filename)
                if os.path.exists(filepath):
                    zipf.write(filepath, filename)
                    print(f"   ✅ {filename}")
            
            # 3. DIRETÓRIOS ESSENCIAIS
            print("\n📂 Diretórios...")
            for dir_path in ESSENTIAL_DIRS:
                full_dir = os.path.join(PROJECT_ROOT, dir_path)
                if os.path.exists(full_dir):
                    count = 0
                    for root, dirs, files in os.walk(full_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, PROJECT_ROOT)
                            zipf.write(file_path, arcname)
                            count += 1
                    print(f"   ✅ {dir_path}/ ({count} arquivos)")
        
        size_mb = os.path.getsize(backup_path) / 1024 / 1024
        print(f"\n{'='*50}")
        print(f"✅ BACKUP CRIADO!")
        print(f"{'='*50}")
        print(f"Arquivo: {backup_filename}")
        print(f"Tamanho: {size_mb:.2f} MB")
        print(f"{'='*50}\n")
        
        return backup_path

    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        return None

# Função de compatibilidade
def create_backup(flask_app=None):
    """Alias para create_backup_lite"""
    return create_backup_lite(flask_app)

def copy_to_cloud(local_backup_path):
    """Copia para Google Drive / OneDrive"""
    # Mesma implementação do original
    cloud_paths = [
        r'G:\Meu Drive',
        r'G:\My Drive',
        os.path.expanduser('~/OneDrive'),
        os.path.expanduser('~/Google Drive')
    ]
    
    for cloud_root in cloud_paths:
        if os.path.exists(cloud_root):
            cloud_dir = os.path.join(cloud_root, "Backups_Gestao_Editais")
            if not os.path.exists(cloud_dir):
                os.makedirs(cloud_dir)
            
            destination = os.path.join(cloud_dir, os.path.basename(local_backup_path))
            shutil.copy2(local_backup_path, destination)
            return destination
    
    return None

def clean_old_backups(directory, days=30):
    """Remove backups antigos"""
    if not os.path.exists(directory):
        return
    
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    
    for filename in os.listdir(directory):
        if filename.endswith('.zip') and 'gestao_editais' in filename:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff:
                    os.remove(file_path)

if __name__ == "__main__":
    backup_path = create_backup_lite()
    if backup_path:
        print(f"\n✅ Teste bem-sucedido!")
        print(f"   {backup_path}")
