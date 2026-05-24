"""
SISTEMA DE BACKUP AUTOMÁTICO - PostgreSQL
==========================================
Versão: 1.0
Data: 29/01/2026
Equipe: Yoko (IA) + Katsuko (Backend Specialist)

Funcionalidades:
- Backup automático do PostgreSQL
- Compressão GZIP para economizar espaço
- Nomenclatura padronizada com timestamp
- Logs de execução
- Verificação de integridade
"""

import subprocess
import os
import gzip
import shutil
from datetime import datetime
import json

class PostgresBackupManager:
    """Gerenciador de backups do PostgreSQL"""
    
    def __init__(self):
        # Configurações do banco (ler do .env em produção)
        self.db_name = 'gestao_editais'
        self.db_user = 'postgres'
        self.db_password = 'admin123'
        self.db_host = 'localhost'
        self.db_port = '5432'
        
        # Diretórios
        self.backup_dir = 'backups/postgres/auto'
        self.log_dir = 'logs/backup'
        
        # Criar diretórios se não existirem
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Caminho do pg_dump
        self.pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
        
    def log(self, message, level='INFO'):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # Salvar em arquivo de log
        log_file = os.path.join(self.log_dir, f"backup_{datetime.now().strftime('%Y%m')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def create_backup(self):
        """Cria backup do PostgreSQL"""
        self.log("=" * 80)
        self.log("🔄 INICIANDO BACKUP AUTOMÁTICO")
        self.log("=" * 80)
        
        # Timestamp para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        compressed_path = backup_path + '.gz'
        
        try:
            # 1. Verificar se pg_dump existe
            if not os.path.exists(self.pg_dump_path):
                self.log(f"ERRO: pg_dump não encontrado em {self.pg_dump_path}", 'ERROR')
                return False
            
            self.log(f"📦 Criando backup: {backup_filename}")
            
            # 2. Executar pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            result = subprocess.run(
                [
                    self.pg_dump_path,
                    '-h', self.db_host,
                    '-p', self.db_port,
                    '-U', self.db_user,
                    '-F', 'p',  # Plain SQL format
                    '-f', backup_path,
                    self.db_name
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            if result.returncode != 0:
                self.log(f"ERRO ao executar pg_dump: {result.stderr}", 'ERROR')
                return False
            
            # 3. Verificar se arquivo foi criado
            if not os.path.exists(backup_path):
                self.log("ERRO: Arquivo de backup não foi criado", 'ERROR')
                return False
            
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            self.log(f"✅ Backup criado: {size_mb:.2f} MB")
            
            # 4. Comprimir com GZIP
            self.log("🗜️  Comprimindo backup...")
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo descomprimido
            os.remove(backup_path)
            
            compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
            compression_ratio = (1 - compressed_size_mb / size_mb) * 100
            
            self.log(f"✅ Comprimido: {compressed_size_mb:.2f} MB (economia de {compression_ratio:.1f}%)")
            
            # 5. Metadados do backup
            metadata = {
                'filename': os.path.basename(compressed_path),
                'timestamp': timestamp,
                'size_mb': round(compressed_size_mb, 2),
                'original_size_mb': round(size_mb, 2),
                'compression_ratio': round(compression_ratio, 1),
                'database': self.db_name,
                'created_at': datetime.now().isoformat()
            }
            
            metadata_file = compressed_path + '.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.log("📋 Metadados salvos")
            self.log("=" * 80)
            self.log("✅ BACKUP CONCLUÍDO COM SUCESSO")
            self.log("=" * 80)
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("ERRO: Timeout ao criar backup (> 5 minutos)", 'ERROR')
            return False
        except Exception as e:
            self.log(f"ERRO INESPERADO: {str(e)}", 'ERROR')
            return False
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sql.gz'):
                filepath = os.path.join(self.backup_dir, file)
                metadata_file = filepath + '.json'
                
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

if __name__ == "__main__":
    manager = PostgresBackupManager()
    success = manager.create_backup()
    
    if success:
        print()
        print("📊 BACKUPS DISPONÍVEIS:")
        print("-" * 80)
        for backup in manager.list_backups()[:5]:  # Mostrar últimos 5
            print(f"  • {backup['filename']} - {backup['size_mb']} MB - {backup['created_at']}")
        exit(0)
    else:
        exit(1)
