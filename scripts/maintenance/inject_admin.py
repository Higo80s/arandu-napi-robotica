# Script para injetar rotas administrativas no app.py

block_path = 'admin_routes_block.py'
app_path = 'app.py'

with open(block_path, 'r', encoding='utf-8') as f:
    new_conent = f.read()

with open(app_path, 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

# Inserir antes do if __name__ == '__main__':
insert_index = -1
for i, line in enumerate(app_lines):
    if "if __name__ ==" in line:
        insert_index = i
        break

if insert_index != -1 and "@app.route('/admin/programas')" not in "".join(app_lines):
    final_lines = app_lines[:insert_index] + [new_conent + "\n"] + app_lines[insert_index:]
    with open(app_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print("✅ Rotas administrativas injetadas com sucesso!")
else:
    print("⚠️ Rotas já existem ou ponto de inserção não encontrado.")
