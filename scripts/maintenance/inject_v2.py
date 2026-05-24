# Script para injetar a rota V2 no app.py

route_file = 'admin_v2_route.py'
app_file = 'app.py'

with open(route_file, 'r', encoding='utf-8') as f:
    route_code = f.read()

with open(app_file, 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

if "@app.route('/admin/programas_v2')" not in "".join(app_lines):
    # Inserir antes do if __name__
    insert_idx = -1
    for i, line in enumerate(app_lines):
        if "if __name__ ==" in line:
            insert_idx = i
            break
            
    if insert_idx != -1:
        final_lines = app_lines[:insert_idx] + ["\n" + route_code + "\n"] + app_lines[insert_idx:]
        with open(app_file, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
        print("✅ Rota V2 injetada!")
    else:
        print("⚠️ Erro: Main block não encontrado.")
else:
    print("⚠️ Rota já existe.")
