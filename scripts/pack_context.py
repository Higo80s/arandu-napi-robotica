import os
import sys

# Paths
base_dir = r"C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo"
output_file = r"C:\Users\higosantos\.gemini\antigravity\brain\fc352bb1-131c-4565-9f22-5c41013ec312\arandu_context_packing.md"

skip_dirs = {'.venv', 'venv', '__pycache__', '.git', 'static', 'node_modules', 'archive', 'docs', 'tests', 'planilnhas_externas', 'instance', 'migrations', 'tempmediaStorage', '.agent', 'core'}

def generate_tree(dir_path, prefix=""):
    tree_str = ""
    try:
        entries = sorted(os.listdir(dir_path))
    except Exception:
        return ""
    
    # Filter entries
    entries = [e for e in entries if e not in skip_dirs and not e.endswith('.pyc') and not e.endswith('.zip') and not e.endswith('.db') and not e.endswith('.txt') and not e.endswith('.sqlite') and not e.endswith('.pyd') and not e.endswith('.log')]
    
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        tree_str += prefix + ("└── " if is_last else "├── ") + entry + "\n"
        if os.path.isdir(path):
            tree_str += generate_tree(path, prefix + ("    " if is_last else "│   "))
    return tree_str

def get_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {e}"

files_to_pack = [
    'app.py',
    'extensions.py',
    'models.py',
    'core/memento.py',
    'core/strategies.py',
    'blueprints/internacionalizacao.py',
    'templates/bolsistas/form.html',
    'templates/bolsistas/index.html',
    'templates/internacionalizacao/dashboard.html'
]

# Add all blueprints
blueprints_dir = os.path.join(base_dir, 'blueprints')
if os.path.exists(blueprints_dir):
    for f in sorted(os.listdir(blueprints_dir)):
        if f.endswith('.py'):
            files_to_pack.append(f'blueprints/{f}')

os.chdir(base_dir)

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("# Master Arquivo de Context Packing - Sistema Arandú\n\n")
    out.write("Este documento contém o código-fonte integral (Backend, Models e Controllers) do sistema.\n\n")
    
    out.write("## Árvore do Projeto\n```text\n")
    out.write("gestao_editais_novo/\n")
    out.write(generate_tree('.'))
    out.write("```\n\n")
    
    out.write("---\n\n")
    
    for relative_path in files_to_pack:
        if os.path.exists(relative_path):
            out.write(f"## Caminho: [{relative_path}]\n\n")
            out.write("```python\n")
            out.write(f"# --- START OF FILE: {os.path.basename(relative_path)} ---\n")
            out.write(get_file_content(relative_path))
            out.write(f"\n# --- END OF FILE: {os.path.basename(relative_path)} ---\n")
            out.write("```\n\n")

print(f"Context packing successfully saved!")
