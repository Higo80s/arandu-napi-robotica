import PyInstaller.__main__
import os
import sys

def build():
    # Detect OS for separator (Windows uses ;)
    separator = ';' if os.name == 'nt' else ':'
    
    # Define arguments
    args = [
        'app.py',
        '--name=GestaoEditais',
        '--onefile',
        '--clean',
        '--noconfirm',
        # Add templates
        f'--add-data=templates{separator}templates',
        # Add static
        f'--add-data=static{separator}static',
        # Hidden imports often missed by hook
        '--hidden-import=sqlalchemy.sql.default_comparator',
        '--hidden-import=reportlab',
        '--hidden-import=openpyxl',
        '--hidden-import=email_validator', # Often needed for validation
    ]
    
    print(f"Starting Build with args: {args}")
    PyInstaller.__main__.run(args)
    print("Build completed successfully.")

if __name__ == "__main__":
    build()
