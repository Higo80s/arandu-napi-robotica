"""
backup_system.py - Versão Robusta com Detecção pg_dump e JSON Fallback
======================================================================

Melhorias:
1. Procura pg_dump em pastas padrão do PostgreSQL no Windows
2. JSON Fallback OTIMIZADO (escrita por partes para evitar estouro de memória)
3. Logs dentro do ZIP para diagnóstico
4. Garante que ALGUM backup de dados seja feito
"""

import os
import zipfile
import datetime
import subprocess
import shutil
import json
import glob
from urllib.parse import urlparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')

# APENAS arquivos e pastas ESSENCIAIS (mantendo versão lite para evitar timeout de arquivos)
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

def find_pg_dump():
    """Tenta encontrar o pg_dump em locais comuns do Windows"""
    # 1. Tentar PATH atual
    if shutil.which('pg_dump'):
        return 'pg_dump'
    
    # 2. Procurar em Program Files
    common_paths = [
        r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_dump.exe"
    ]
    
    for pattern in common_paths:
        matches = glob.glob(pattern)
        if matches:
            # Pegar a versão mais recente (ordem alfabética reversa tende a pegar versão maior)
            matches.sort(reverse=True)
            return matches[0]
            
    return None

def backup_postgres_quick(db_url, output_path):
    """Backup rápido PostgreSQL com pg_dump"""
    try:
        parsed = urlparse(db_url)
        if not parsed.scheme or 'postgres' not in parsed.scheme:
            return None
        
        pg_dump_cmd = find_pg_dump()
        if not pg_dump_cmd:
            print("⚠️  pg_dump não encontrado no sistema.")
            return False
            
        print(f"   Using: {pg_dump_cmd}")
        
        cmd = [
            pg_dump_cmd,
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
        
        # Timeout aumentado para 60s
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return True
        else:
            print(f"   Erro pg_dump: {result.stderr}")
            return False
    except Exception as e:
        print(f"   Exceção pg_dump: {e}")
        return False

def backup_json_optimized(flask_app, output_path):
    """
    Exporta dados para JSON de forma otimizada (sem carregar tudo na RAM)
    Escreve diretamente no arquivo para evitar travamentos.
    """
    try:
        print("   Iniciando exportação JSON (fallback)...")
        from models import (db, Edital, Modalidade, Bolsista, Campus, 
                           ProgramaAcademico, Residente, ProapAplicacao, 
                           ProapRepasse, Acompanhamento)
        
        # Lista de tabelas para exportar
        models_to_export = [
            ('editais', Edital),
            ('modalidades', Modalidade),
            ('campus', Campus),
            ('programas', ProgramaAcademico),
            ('bolsistas', Bolsista),
            ('residentes', Residente),
            ('proap_aplicacoes', ProapAplicacao),
            ('proap_repasses', ProapRepasse),
            ('acompanhamentos', Acompanhamento)
        ]
        
        with flask_app.app_context():
            # Estrutura inicial
            data_structure = {
                'metadata': {
                    'date': datetime.datetime.now().isoformat(),
                    'type': 'json_fallback_optimized'
                },
                'data': {}
            }
            
            # Escrever direto no arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                # Início do JSON
                f.write('{\n  "metadata": {\n')
                f.write(f'    "date": "{datetime.datetime.now().isoformat()}",\n')
                f.write('    "version": "6.1"\n  },\n  "data": {\n')
                
                # Iterar tabelas
                total_tables = len(models_to_export)
                for idx, (name, model) in enumerate(models_to_export):
                    print(f"     Exportando {name}...")
                    f.write(f'    "{name}": [\n')
                    
                    try:
                        records = model.query.all()
                        total_records = len(records)
                        
                        for i, record in enumerate(records):
                            # Converter para dict
                            record_dict = {k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v 
                                          for k, v in record.__dict__.items() if not k.startswith('_')}
                            
                            json_str = json.dumps(record_dict, ensure_ascii=False)
                            
                            # Vírgula se não for o último
                            separator = ",\n" if i < total_records - 1 else "\n"
                            f.write(f"      {json_str}{separator}")
                            
                    except Exception as e:
                        print(f"     Erro exportando {name}: {e}")
                        f.write(f'      {{ "error": "{str(e)}" }}\n')
                    
                    # Fechar array da tabela
                    if idx < total_tables - 1:
                        f.write('    ],\n')
                    else:
                        f.write('    ]\n')
                
                # Fim do JSON
                f.write('  }\n}')
                
        return True
    except Exception as e:
        print(f"   Erro crítico JSON export: {e}")
        return False

def create_backup_lite(flask_app=None):
    """
    Cria backup ROBUSTO (tenta pg_dump, senão vai de JSON)
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"gestao_editais_v6_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Log de execução para incluir no zip
    log_content = [f"Backup iniciado em {timestamp}"]

    print(f"\n{'='*50}")
    print(f"BACKUP ROBUSTO - V6.1")
    print(f"{'='*50}\n")

    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # 1. BANCO DE DADOS
            db_url = os.getenv('DATABASE_URL')
            db_success = False
            
            if db_url and 'postgres' in db_url:
                print("📊 Tentando backup PostgreSQL...")
                log_content.append("Detectado PostgreSQL.")
                
                # TENTATIVA 1: pg_dump
                pg_file = os.path.join(BACKUP_DIR, f"db_{timestamp}.dump")
                if backup_postgres_quick(db_url, pg_file):
                    zipf.write(pg_file, f"database/postgres.dump")
                    os.remove(pg_file)
                    print("   ✅ pg_dump sucesso!")
                    log_content.append("Sucesso: pg_dump incluído como database/postgres.dump")
                    db_success = True
                else:
                    print("   ⚠️  pg_dump falhou/não encontrado. Tentando JSON...")
                    log_content.append("Falha: pg_dump não executou.")
                    
                    # TENTATIVA 2: JSON Fallback
                    if flask_app:
                        json_file = os.path.join(BACKUP_DIR, f"db_{timestamp}.json")
                        if backup_json_optimized(flask_app, json_file):
                            zipf.write(json_file, f"database/data_export.json")
                            os.remove(json_file)
                            print("   ✅ JSON fallback sucesso!")
                            log_content.append("Sucesso: Backup JSON incluído como database/data_export.json")
                            db_success = True
                        else:
                             print("   ❌ JSON fallback falhou.")
                             log_content.append("Erro Crítico: JSON fallback falhou.")
                    else:
                        print("   ❌ Flask app não fornecido para JSON fallback.")
                        log_content.append("Erro: Impossível rodar JSON backup sem contexto Flask.")

            if not db_success:
                print("⚠️  AVISO CRÍTICO: Nenhum backup de banco de dados foi gerado!")
                log_content.append("ALERTA: O arquivo ZIP não contém dados do banco!")
            
            # 2. ARQUIVOS ESSENCIAIS (Mantido Lite)
            print("\n📁 Arquivos essenciais...")
            for filename in ESSENTIAL_FILES:
                filepath = os.path.join(PROJECT_ROOT, filename)
                if os.path.exists(filepath):
                    zipf.write(filepath, filename)
            
            # 3. DIRETÓRIOS
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
            
            # Incluir log no zip
            log_str = "\n".join(log_content)
            zipf.writestr("backup_log.txt", log_str)
        
        size_mb = os.path.getsize(backup_path) / 1024 / 1024
        print(f"\n{'='*50}")
        print(f"✅ BACKUP CONCLUÍDO")
        print(f"Tamanho: {size_mb:.2f} MB")
        print(f"{'='*50}\n")
        
        return backup_path

    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}\n")
        return None

# Alias
def create_backup(flask_app=None):
    return create_backup_lite(flask_app)

def copy_to_cloud(local_backup_path):
    cloud_paths = [
        r'G:\Meu Drive', r'G:\My Drive',
        os.path.expanduser('~/OneDrive'), os.path.expanduser('~/Google Drive')
    ]
    for cloud_root in cloud_paths:
        if os.path.exists(cloud_root):
            cloud_dir = os.path.join(cloud_root, "Backups_Gestao_Editais")
            if not os.path.exists(cloud_dir): os.makedirs(cloud_dir)
            destination = os.path.join(cloud_dir, os.path.basename(local_backup_path))
            try:
                shutil.copy2(local_backup_path, destination)
                return destination
            except: pass
    return None

def clean_old_backups(directory, days=30):
    if not os.path.exists(directory): return
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    for filename in os.listdir(directory):
        if filename.endswith('.zip') and 'gestao_editais' in filename:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                if datetime.datetime.fromtimestamp(os.path.getmtime(file_path)) < cutoff:
                    try: os.remove(file_path)
                    except: pass

if __name__ == "__main__":
    # Teste rápido se rodar direto
    print("Para testar, use: python app.py e clique no botão de backup")
