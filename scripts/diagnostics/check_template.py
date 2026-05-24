import os
from app_flask import app

print("--- TEMPLATE DIAGNOSTIC ---")
template_folder = app.template_folder
if not os.path.isabs(template_folder):
    template_folder = os.path.join(app.root_path, template_folder)

print(f"Template Folder: {template_folder}")

bolsistas_idx = os.path.join(template_folder, 'bolsistas', 'index.html')
if os.path.exists(bolsistas_idx):
    print("bolsistas/index.html found.")
    with open(bolsistas_idx, 'r', encoding='utf-8') as f:
        content = f.read()
        if '({{ bolsista.status }})' in content:
            print("SUCCESS: Debug text FOUND in index.html")
        else:
            print("FAILURE: Debug text NOT FOUND in index.html")
else:
    print("bolsistas/index.html NOT FOUND!")

print("--- END TEMPLATE DIAGNOSTIC ---")
