"""
LIMPEZA AUTOMÁTICA DE BACKUPS ANTIGOS
======================================
Versão: 1.0
Data: 29/01/2026
Equipe: Yoko (IA) + Katsuko (Backend Specialist)

Funcionalidades:
- Remove backups com mais de N dias
- Mantém sempre os últimos X backups (segurança)
- Log de remoções
- Modo dry-run para preview
"""

import os
from datetime import datetime, timedelta
import json

class BackupCleanupManager:
    """Gerenciador de limpeza de backups"""
    
    def __init__(self, retention_days=30, min_backups_keep=7):
        """
        Args:
            retention_days: Número de dias para manter backups
            min_backups_keep: Número mínimo de backups a sempre manter
        """
        self.backup_dir = 'backups/postgres/auto'
        self.log_dir = 'logs/backup'
        self.retention_days = retention_days
        self.min_backups_keep = min_backups_keep
        
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        log_file = os.path.join(self.log_dir, f"cleanup_{datetime.now().strftime('%Y%m')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def get_backups(self):
        """Lista todos os backups com informações de data"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sql.gz'):
                filepath = os.path.join(self.backup_dir, file)
                
                backup_info = {
                    'filename': file,
                    'filepath': filepath,
                    'created_at': datetime.fromtimestamp(os.path.getctime(filepath)),
                    'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'metadata_file': filepath + '.json'
                }
                
                backups.append(backup_info)
        
        # Ordenar por data (mais recente primeiro)
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def cleanup(self, dry_run=False):
        """
        Remove backups antigos
        
        Args:
            dry_run: Se True, apenas simula a remoção sem deletar
        """
        self.log("=" * 80)
        self.log(f"🧹 LIMPEZA DE BACKUPS {'(DRY RUN)' if dry_run else ''}")
        self.log("=" * 80)
        self.log(f"Política: Manter últimos {self.retention_days} dias")
        self.log(f"Segurança: Manter no mínimo {self.min_backups_keep} backups")
        self.log("")
        
        backups = self.get_backups()
        
        if not backups:
            self.log("ℹ️  Nenhum backup encontrado.")
            return
        
        self.log(f"📊 Total de backups: {len(backups)}")
        
        # Data limite
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        self.log(f"📅 Data limite: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
        
        # Identificar backups a remover
        to_remove = []
        to_keep_recent = backups[:self.min_backups_keep]  # Sempre manter os N mais recentes
        
        for backup in backups:
            # Manter se for um dos N mais recentes
            if backup in to_keep_recent:
                continue
            
            # Remover se for mais antigo que a data limite
            if backup['created_at'] < cutoff_date:
                to_remove.append(backup)
        
        if not to_remove:
            self.log("✅ Nenhum backup precisa ser removido.")
            self.log(f"ℹ️  Todos os {len(backups)} backups estão dentro da política.")
            return
        
        self.log(f"🗑️  Backups a remover: {len(to_remove)}")
        self.log("")
        
        total_freed_mb = 0
        
        for backup in to_remove:
            age_days = (datetime.now() - backup['created_at']).days
            
            if dry_run:
                self.log(f"  [DRY RUN] Removeria: {backup['filename']}")
                self.log(f"            Idade: {age_days} dias | Tamanho: {backup['size_mb']} MB")
            else:
                try:
                    # Remover arquivo .sql.gz
                    os.remove(backup['filepath'])
                    
                    # Remover metadata .json se existir
                    if os.path.exists(backup['metadata_file']):
                        os.remove(backup['metadata_file'])
                    
                    total_freed_mb += backup['size_mb']
                    
                    self.log(f"  ✅ Removido: {backup['filename']}")
                    self.log(f"     Idade: {age_days} dias | Tamanho: {backup['size_mb']} MB")
                    
                except Exception as e:
                    self.log(f"  ❌ ERRO ao remover {backup['filename']}: {str(e)}")
        
        self.log("")
        self.log("=" * 80)
        
        if dry_run:
            self.log(f"[DRY RUN] Espaço que seria liberado: {total_freed_mb:.2f} MB")
        else:
            self.log(f"✅ LIMPEZA CONCLUÍDA")
            self.log(f"💾 Espaço liberado: {total_freed_mb:.2f} MB")
            self.log(f"📊 Backups restantes: {len(backups) - len(to_remove)}")
        
        self.log("=" * 80)

if __name__ == "__main__":
    import sys
    
    # Parâmetros
    retention_days = 30  # Padrão: 30 dias
    min_keep = 7         # Sempre manter os 7 últimos
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    # Override via argumentos
    if '--days' in sys.argv:
        try:
            idx = sys.argv.index('--days')
            retention_days = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ Uso: --days <número>")
            exit(1)
    
    manager = BackupCleanupManager(
        retention_days=retention_days,
        min_backups_keep=min_keep
    )
    
    manager.cleanup(dry_run=dry_run)
