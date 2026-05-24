import os
import hashlib

def calculate_hash_and_extract(directory, output_file="INPI_CODIGO_FONTE.txt"):
    """
    1. Calcula o HASH SHA-256 de todo o projeto (para criptografia visual).
    2. Extrai as primeiras e últimas linhas do código (Exigência visual do INPI).
    """
    
    print(f"--- PREPARANDO ARQUIVOS PARA INPI ---")
    print(f"Diretório base: {directory}")
    
    sha256_hash = hashlib.sha256()
    source_content = []
    
    # Lista de arquivos principais para "Provar" autoria
    # Focamos nos arquivos Core
    priority_files = [
        'app.py',
        'models.py',
        'requirements.txt',
        'Dockerfile',
        'templates/base.html',
        'templates/dashboard.html'
    ]

    print(f"\n1. CALCULANDO HASH (SHA-256)...")
    
    total_files = 0
    for root, dirs, files in os.walk(directory):
        # Ignorar pastas de sistema/binários
        if '.git' in root or '.venv' in root or '__pycache__' in root or 'instance' in root:
            continue
            
        for filename in files:
            # Ignorar arquivos binários/db
            if filename.endswith(('.db', '.pyc', '.pdf', '.png', '.jpg', '.zip')):
                continue
                
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "rb") as f:
                    # Ler em chunks para não estourar memória
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                total_files += 1
            except Exception as e:
                print(f"Erro lendo {filename}: {e}")

    final_hash = sha256_hash.hexdigest()
    print(f"✅ HASH GERADO: {final_hash}")
    
    print(f"\n2. GERANDO ARQUIVO DE TEXTO (Para transformar em PDF)...")
    
    with open(output_file, "w", encoding='utf-8') as outfile:
        outfile.write("REGISTRO DE PROGRAMA DE COMPUTADOR - INPI\n")
        outfile.write("=========================================\n\n")
        outfile.write(f"SISTEMA: Gestão de Editais (Versão 11.4)\n")
        outfile.write(f"HASH SHA-256 DO PROJETO: {final_hash}\n")
        outfile.write(f"DATA GERAÇÃO: {os.popen('date').read().strip() if os.name != 'nt' else ''}\n\n")
        outfile.write("--- INÍCIO DO CÓDIGO FONTE (AMOSTRAGEM) ---\n\n")
        
        for p_file in priority_files:
            full_path = os.path.join(directory, p_file)
            if os.path.exists(full_path):
                outfile.write(f"ARQUIVO: {p_file}\n")
                outfile.write("-" * 40 + "\n")
                try:
                    with open(full_path, "r", encoding='utf-8') as f:
                        lines = f.readlines()
                        # INPI pede "Trechos" suficientes para caracterizar.
                        # Vamos colocar os primeiros 50 linhas de cada arquivo core.
                        for i, line in enumerate(lines[:100]):
                            outfile.write(f"{i+1:04d}: {line}")
                        if len(lines) > 100:
                            outfile.write("\n... [CÓDIGO CONTINUA] ...\n")
                except Exception as e:
                    outfile.write(f"[ERRO LENDO ARQUIVO]: {e}\n")
                outfile.write("\n" + "="*40 + "\n\n")

    print(f"✅ Arquivo gerado: {output_file}")
    print(f"👉 Converta este arquivo para PDF. Ele servirá como a 'Listagem do Código Fonte'.")
    print(f"👉 O HASH ({final_hash}) deve ser copiado no formulário do INPI.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calculate_hash_and_extract(current_dir, os.path.join(current_dir, "docs", "INPI_FONTE_PARA_PDF.txt"))
