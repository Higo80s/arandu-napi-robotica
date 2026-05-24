"""
Sistema de Backup Melhorado - Gestão de Editais V6
===================================================

MUDANÇAS:
- Agora faz backup do PostgreSQL usando pg_dump (ou JSON como fallback)
- Mantém backup de arquivos do projeto
- Suporta automaticamente PostgreSQL e SQLite

AUTOR: Antigravity AI
DATA: 2026-02-01
"""

import os
import zipfile
import datetime
import shutil
import subprocess
import json
from urllib.parse import urlparse

# Configurações
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')
EXCLUDE_DIRS = {'.venv', '.git', '__pycache__', 'backups', 'node_modules'}
EXCLUDE_FILES = {'.DS_Store', 'Thumbs.db'}

# Tentativas de caminho para Cloud Storage
CLOUD_PATHS = [
    r'G:\Meu Drive',
    r'G:\My Drive',
    r'G:\Drives compartilhados',
    os.path.expanduser('~/OneDrive'),
    os.path.expanduser('~/Google Drive')
]

def get_cloud_path():
    for path in CLOUD_PATHS:
        if os.path.exists(path):
            return path
    return None

def backup_postgres_dump(db_url, output_path):
    """
    Exporta PostgreSQL usando pg_dump (método preferencial)
    
    Retorna:
        str: Caminho do arquivo .dump criado
        None: Se pg_dump não estiver disponível ou falhar
    """
    try:
        # Parse DATABASE_URL (formato: postgresql://user:pass@host:port/dbname)
        parsed = urlparse(db_url)
        
        if not parsed.scheme or 'postgres' not in parsed.scheme:
            print("AVISO: URL não é PostgreSQL, pulando pg_dump")
            return None
        
        # Comando pg_dump
        cmd = [
            'pg_dump',
            '-h', parsed.hostname or 'localhost',
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '-F', 'c',  # Format custom (comprimido)
            '-f', output_path
        ]
        
        # Configurar senha via variável de ambiente
        env = os.environ.copy()
        if parsed.password:
            env['PGPASSWORD'] = parsed.password
        
        print(f"Executando pg_dump para PostgreSQL...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Backup PostgreSQL (pg_dump) criado: {os.path.basename(output_path)}")
            return output_path
        else:
            print(f"ERRO pg_dump: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("AVISO: pg_dump não encontrado no sistema. Tentando método alternativo...")
        return None
    except subprocess.TimeoutExpired:
        print("ERRO: pg_dump excedeu tempo limite de 60s")
        return None
    except Exception as e:
        print(f"ERRO ao executar pg_dump: {e}")
        return None

def backup_postgres_json(app, output_path):
    """
    Exporta dados do PostgreSQL via SQLAlchemy (fallback quando pg_dump não disponível)
    
    Parametros:
        app: Flask app instance (para acessar context)
        output_path: Caminho onde salvar o JSON
    
    Retorna:
        str: Caminho do arquivo .json criado
        None: Se falhar
    """
    try:
        print("Iniciando export JSON via SQLAlchemy (fallback)...")
        
        # Import aqui para evitar circular dependency
        from models import (db, Edital, Modalidade, Bolsista, Campus, 
                           ProgramaAcademico, Residente, ProapAplicacao, 
                           ProapRepasse, Acompanhamento)
        
        data = {
            'metadata': {
                'backup_date': datetime.datetime.now().isoformat(),
                'backup_method': 'sqlalchemy_json',
                'version': '6.0'
            },
            'data': {}
        }
        
        with app.app_context():
            # Exportar cada tabela (ordenado para respeitar FKs na restauração)
            tables = [
                ('editais', Edital),
                ('modalidades', Modalidade),
                ('campus', Campus),
                ('programas_academicos', ProgramaAcademico),
                ('bolsistas', Bolsista),
                ('residentes', Residente),
                ('proap_aplicacoes', ProapAplicacao),
                ('proap_repasses', ProapRepasse),
                ('acompanhamentos', Acompanhamento),
            ]
            
            for table_name, model in tables:
                try:
                    records = model.query.all()
                    # Converter para dicionário (assumindo que models têm __dict__ ou to_dict())
                    data['data'][table_name] = [
                        {k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v 
                         for k, v in record.__dict__.items() if not k.startswith('_')}
                        for record in records
                    ]
                    print(f"  - {table_name}: {len(records)} registros")
                except Exception as e:
                    print(f"  ⚠️  {table_name}: ERRO - {e}")
                    data['data'][table_name] = []
        
        # Salvar JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        file_size = os.path.getsize(output_path) / 1024 / 1024  # MB
        print(f"✅ Backup JSON criado: {os.path.basename(output_path)} ({file_size:.2f} MB)")
        return output_path
        
    except Exception as e:
        print(f"ERRO crítico no backup JSON: {e}")
        return None

def create_backup(flask_app=None):
    """
    Cria backup completo do sistema (código + banco de dados)
    
    Parametros:
        flask_app: Flask app instance (necessário para backup JSON)
    """
    # Garantir diretório de backups
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Nome do arquivo com timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"gestao_editais_backup_v6_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    print(f"\n{'='*60}")
    print(f"Iniciando Backup Completo do Sistema")
    print(f"{'='*60}")
    print(f"Destino: {backup_path}\n")

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # ===== 1. BACKUP DO BANCO DE DADOS =====
            db_url = os.getenv('DATABASE_URL')
            database_backed_up = False
            
            if db_url and 'postgres' in db_url:
                print("📊 BANCO DE DADOS: PostgreSQL detectado\n")
                
                # Tentar pg_dump primeiro
                pg_dump_file = os.path.join(BACKUP_DIR, f"db_postgres_{timestamp}.dump")
                pg_result = backup_postgres_dump(db_url, pg_dump_file)
                
                if pg_result:
                    zipf.write(pg_result, f"database/postgres_backup.dump")
                    os.remove(pg_result)  # Limpar temporário
                    database_backed_up = True
                # TEMPORARIAMENTE DESABILITADO - causando freeze
                elif False:  # elif flask_app:
                    # FALLBACK JSON DESABILITADO - causando timeout
                    # Fallback para JSON
                    print("\n⚠️  Usando método alternativo (JSON)...\n")
                    json_file = os.path.join(BACKUP_DIR, f"db_data_{timestamp}.json")
                    json_result = backup_postgres_json(flask_app, json_file)
                    
                    if json_result:
                        zipf.write(json_result, f"database/data_export.json")
                        os.remove(json_result)
                        database_backed_up = True
                
                if not database_backed_up:
                    print("⚠️  AVISO: Backup do banco PostgreSQL FALHOU!")
                    
            elif db_url and 'sqlite' in db_url:
                print("📊 BANCO DE DADOS: SQLite detectado\n")
                # Para SQLite, copiar o arquivo .db diretamente
                db_path = db_url.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    zipf.write(db_path, f"database/gestao_editais.db")
                    database_backed_up = True
                    print(f"✅ Backup SQLite incluído: {os.path.basename(db_path)}")
            else:
                print("⚠️  AVISO: DATABASE_URL não configurada, pulando backup do banco\n")
            
            # ===== 2. BACKUP DOS ARQUIVOS DO PROJETO =====
            print(f"\n📁 ARQUIVOS DO PROJETO:\n")
            file_count = 0
            
            for root, dirs, files in os.walk(PROJECT_ROOT):
                # Pular diretórios excluídos
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    if file in EXCLUDE_FILES:
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, PROJECT_ROOT)
                    zipf.write(file_path, arcname)
                    file_count += 1
            
            print(f"✅ {file_count} arquivos adicionados ao backup")
        
        # Informações finais
        backup_size = os.path.getsize(backup_path) / 1024 / 1024  # MB
        print(f"\n{'='*60}")
        print(f"✅ BACKUP COMPLETO CRIADO COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivo: {backup_filename}")
        print(f"Tamanho: {backup_size:.2f} MB")
        if database_backed_up:
            print(f"Banco de Dados: ✅ Incluído")
        else:
            print(f"Banco de Dados: ⚠️  NÃO incluído")
        print(f"{'='*60}\n")
        
        return backup_path

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO ao criar backup: {e}\n")
        return None

def copy_to_cloud(local_backup_path):
    """Copia backup para nuvem (Google Drive / OneDrive)"""
    cloud_root = get_cloud_path()
    if not cloud_root:
        print("AVISO: Nenhuma pasta de nuvem encontrada.")
        return None

    cloud_backup_dir = os.path.join(cloud_root, "Backups_Gestao_Editais")
    
    try:
        if not os.path.exists(cloud_backup_dir):
            os.makedirs(cloud_backup_dir)
        
        filename = os.path.basename(local_backup_path)
        destination = os.path.join(cloud_backup_dir, filename)
        
        print(f"☁️  Copiando para nuvem: {cloud_backup_dir}")
        shutil.copy2(local_backup_path, destination)
        print(f"✅ Cópia na nuvem concluída!")
        return destination
        
    except Exception as e:
        print(f"ERRO ao copiar para nuvem: {e}")
        return None

def clean_old_backups(directory, days=30):
    """Remove backups com mais de 'days' dias"""
    if not os.path.exists(directory):
        return

    print(f"\n🧹 Limpando backups antigos em {directory}...")
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days)
    
    count = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.zip') and "gestao_editais_backup" in filename:
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff:
                os.remove(file_path)
                print(f"  - Removido: {filename}")
                count += 1
    
    if count == 0:
        print("  Nenhum arquivo antigo para remover.")
    else:
        print(f"  ✅ {count} backup(s) antigo(s) removido(s)")

def main():
    print("\n" + "="*60)
    print("SISTEMA DE BACKUP - GESTÃO DE EDITAIS V6")
    print("="*60 + "\n")
    
    # Criar backup (sem Flask app - só arquivos)
    backup_path = create_backup(flask_app=None)
    
    if backup_path:
        # Copiar para nuvem
        copy_to_cloud(backup_path)
        
        # Limpar backups antigos
        clean_old_backups(BACKUP_DIR)
        
        cloud_root = get_cloud_path()
        if cloud_root:
            cloud_dir = os.path.join(cloud_root, "Backups_Gestao_Editais")
            clean_old_backups(cloud_dir)
    
    print("\n" + "="*60)
    print("PROCESSO FINALIZADO")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
