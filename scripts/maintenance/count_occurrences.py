path = 'app.py'
try:
    with open(path, 'rb') as f: # Ler como binário para evitar encoding issues
        content = f.read()

    # Procurar por bytes
    termo = b'def admin_consolidado'
    count = content.count(termo)
    print(f"Total de 'def admin_consolidado': {count}")
    
    termo_old = b'get_consolidated_stats'
    count_old = content.count(termo_old)
    print(f"Total de 'get_consolidated_stats': {count_old}")

except Exception as e:
    print(e)
