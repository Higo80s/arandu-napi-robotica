import os
import zipfile
import hashlib
import shutil

# Configurações do Registro v11.21
PROJECT_NAME = "arandu_source_v11.zip"
DIST_DIR = "dist"
SOURCE_DIR = "." # Diretório atual do projeto

# Padrões de Exclusão (Segurança e Limpeza)
EXCLUDE_PATTERNS = [
    ".git", ".env", "__pycache__", ".venv", "venv", "env", "node_modules", 
    ".bak", ".old", ".gemini", ".history", "dist", "tmp",
    "*.db", "*.sqlite", ".vscode", ".idea", "*.pyc"
]

def should_exclude(path):
    """
    Verifica se o caminho (arquivo ou diretório) deve ser excluído do pacote.
    """
    path_norm = path.replace("\\", "/")
    parts = path_norm.split("/")
    
    for pattern in EXCLUDE_PATTERNS:
        if "*" in pattern:
            import fnmatch
            if any(fnmatch.fnmatch(p, pattern) for p in parts):
                return True
        else:
            if pattern in parts:
                return True
    return False

def prepare_package():
    print(f"📦 Iniciando Consolidação do Pacote: {PROJECT_NAME}")
    
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)
    
    zip_path = os.path.join(DIST_DIR, PROJECT_NAME)
    
    # Criar o arquivo ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Filtrar diretórios in-place para o os.walk
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path):
                    # Caminho relativo dentro do ZIP
                    arcname = os.path.relpath(file_path, SOURCE_DIR)
                    zipf.write(file_path, arcname)
                    file_count += 1
    
    print(f"✅ Arquivo {PROJECT_NAME} gerado com {file_count} arquivos.")
    
    # Gerar Hash SHA-512
    sha512_hash = hashlib.sha512()
    with open(zip_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha512_hash.update(byte_block)
    
    hex_digest = sha512_hash.hexdigest().upper()
    print("\n" + "="*70)
    print("💎 RESUMO DIGITAL (HASH SHA-512) - HEXADECIMAL CONTÍNUO:")
    print(hex_digest)
    print("="*70 + "\n")
    
    return hex_digest

if __name__ == "__main__":
    prepare_package()
