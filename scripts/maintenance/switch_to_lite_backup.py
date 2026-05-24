"""
Substitui backup_system.py pelo lite version
"""

import shutil
import os

# Fazer backup do original
if os.path.exists('backup_system.py'):
    shutil.copy2('backup_system.py', 'backup_system_OLD.py')
    print("✅ Backup do original: backup_system_OLD.py")

# Substituir pelo lite
shutil.copy2('backup_system_lite.py', 'backup_system.py')
print("✅ backup_system.py substituído pela versão LITE")

print("\n📊 Diferenças:")
print("   ANTES: Backup completo de TODOS os arquivos (lento)")
print("   AGORA: Backup apenas essenciais (rápido, < 5s)")

print("\n✅ Teste novamente o botão Fazer Backup!")
