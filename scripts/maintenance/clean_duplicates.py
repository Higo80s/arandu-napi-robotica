# Script para limpar duplicatas no app.py

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
seen_consolidado = False
seen_download = False

skip = False

for line in lines:
    # Detecta definições
    if "def admin_consolidado():" in line:
        if seen_consolidado:
            skip = True # Já vi uma vez, pular as próximas
        seen_consolidado = True
        
    if "def download_consolidado():" in line:
        if seen_download:
            skip = True
        seen_download = True

    # Se estivermos pulando, verificar se acabou a função (indentação ou novo decorator)
    if skip:
        if line.strip() == "" or line.startswith("@") or  (len(line) > 0 and line[0] not in [' ', '\t', '#']):
             # Parece que acabou a função duplicada, mas cuidado para não deletar a próxima rota
             if line.startswith("@") or "if __name__" in line:
                 skip = False
    
    if not skip:
        new_lines.append(line)

# Salvar
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Duplicatas limpas!")
