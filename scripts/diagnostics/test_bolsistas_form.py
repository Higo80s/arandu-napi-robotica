import requests

try:
    r = requests.get('http://127.0.0.1:5003/bolsistas/novo')
    print(f'Status: {r.status_code}')
    
    # Count editais in dropdown
    import re
    editais = len(re.findall(r'<option value="\d+"', r.text))
    campus = len(re.findall(r'data-campus-id="\d+"', r.text))
    
    print(f'Editais no dropdown: {editais}')
    print(f'Programas no dropdown: {campus}')
    
    if editais > 0:
        print('✅ Dropdown de editais está populado!')
    else:
        print('❌ Dropdown de editais está vazio')
        
except Exception as e:
    print(f'Erro: {e}')
