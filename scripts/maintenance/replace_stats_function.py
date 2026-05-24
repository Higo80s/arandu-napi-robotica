# Script para substituir a função get_consolidated_stats antiga

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False

# Ler novo código
with open('stats_update.py', 'r', encoding='utf-8') as f:
    new_code = f.readlines()

for line in lines:
    if "def get_consolidated_stats():" in line:
        skip = True
    
    if skip and ("@app.route" in line or "if __name__" in line):
        skip = False
        # Inserir novo código aqui
        new_lines.extend(new_code)
    
    if not skip:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Função substituída com sucesso!")
