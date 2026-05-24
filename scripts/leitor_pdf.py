import pyttsx3
import pypdf
import os
import sys
import glob

def init_engine():
    engine = pyttsx3.init()
    # Ajustar velocidade da fala
    engine.setProperty('rate', 170)
    # Tentar selecionar uma voz em português se disponível
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'brazil' in voice.name.lower() or 'portuguese' in voice.name.lower() or 'pt-br' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine

def list_pdfs(root_dir='.'):
    pdf_files = []
    # Busca recursiva por PDFs, excluindo venv e node_modules
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in dirs: dirs.remove('venv')
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def read_pdf(pdf_path, engine):
    print(f"\n--- Lendo: {pdf_path} ---\n")
    try:
        reader = pypdf.PdfReader(pdf_path)
        number_of_pages = len(reader.pages)
        print(f"Total de páginas: {number_of_pages}")
        
        start_page = input("Deseja começar de qual página? (1 para o início): ").strip()
        try:
            current_page_idx = int(start_page) - 1
        except ValueError:
            current_page_idx = 0
            
        if current_page_idx < 0: current_page_idx = 0

        for i in range(current_page_idx, number_of_pages):
            page = reader.pages[i]
            text = page.extract_text()
            
            print(f"\n[Página {i+1}]\n")
            print(text)
            
            # Limpar um pouco texto para evitar leitura estranha de caracteres isolados
            # Mas pyttsx3 geralmente lida bem.
            
            if text.strip():
                engine.say(text)
                engine.runAndWait()
            else:
                print("(Página vazia ou apenas imagens)")
            
            # Controle de navegação
            check = input("\nPressione Enter para próxima página (ou 'q' para sair): ")
            if check.lower() == 'q':
                break
            
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")

def main():
    print("=== Leitor de PDF com Voz ===")
    
    pdfs = list_pdfs(os.getcwd())
    
    if not pdfs:
        print("Nenhum PDF encontrado na pasta atual.")
        target = input("Digite o caminho completo de um PDF: ").strip()
        if os.path.exists(target) and target.lower().endswith('.pdf'):
            path = target
        else:
            print("Arquivo não encontrado.")
            return
    else:
        print("\nPDFs encontrados:")
        for idx, pdf in enumerate(pdfs):
            print(f"{idx + 1}. {pdf}")
        
        print(f"{len(pdfs) + 1}. Digitar outro caminho")
        
        choice = input("\nEscolha o número do PDF para ler: ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(pdfs):
                path = pdfs[choice_idx]
            else:
                path = input("Digite o caminho completo do PDF: ").strip()
        except ValueError:
            path = input("Digite o caminho completo do PDF: ").strip()
    
    if os.path.exists(path):
        engine = init_engine()
        read_pdf(path, engine)
        print("\nLeitura finalizada.")
    else:
        print("Arquivo inválido.")

if __name__ == "__main__":
    main()
