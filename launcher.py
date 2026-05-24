import tkinter as tk
from tkinter import ttk
import threading
import time
import webbrowser
import subprocess
import sys
import os
import requests

def iniciar_servidor():
    """Inicia o servidor Flask em background"""
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW
    else:
        creationflags = 0
        
    python_exec = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exec):
        python_exec = sys.executable
        
    subprocess.Popen([python_exec, "app.py"], creationflags=creationflags)

def verificar_servidor():
    """Verifica se o servidor já está respondendo"""
    try:
        requests.get("http://127.0.0.1:5003", timeout=1)
        return True
    except:
        return False

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("Gestão de Editais - PROAP/PROPPG")
        
        # Remover bordas
        self.overrideredirect(True)
        
        # Dimensões e centralização
        width = 600
        height = 350
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Estilo moderno
        self.configure(bg='#1e3a8a') # Azul escuro institucional
        
        # Frame principal
        main_frame = tk.Frame(self, bg='#1e3a8a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título do Programa
        tk.Label(
            main_frame, 
            text="GESTÃO DE EDITAIS", 
            font=("Segoe UI", 24, "bold"), 
            bg='#1e3a8a', 
            fg='white'
        ).pack(pady=(40, 5))
        
        tk.Label(
            main_frame, 
            text="SISTEMA DE GERENCIAMENTO DE BOLSAS", 
            font=("Segoe UI", 12), 
            bg='#1e3a8a', 
            fg='#93c5fd'
        ).pack(pady=(0, 40))
        
        # Status
        self.status_label = tk.Label(
            main_frame, 
            text="Iniciando sistema...", 
            font=("Segoe UI", 10), 
            bg='#1e3a8a', 
            fg='white'
        )
        self.status_label.pack(side='bottom', pady=(0, 20))
        
        # Barra de progresso customizada
        self.progress = ttk.Progressbar(
            main_frame, 
            orient='horizontal', 
            length=400, 
            mode='determinate'
        )
        self.progress.pack(side='bottom', pady=(0, 10))
        
        # Iniciar processo
        self.progresso = 0
        threading.Thread(target=self.carregar_sistema, daemon=True).start()

    def carregar_sistema(self):
        etapas = [
            ("Verificando ambiente...", 10, 0.5),
            ("Carregando módulos...", 30, 0.8),
            ("Conectando ao banco de dados...", 50, 0.8),
            ("Iniciando servidor Flask...", 70, 0.5),
            ("Aguardando resposta...", 90, 0)
        ]
        
        iniciar_servidor()
        
        for texto, valor, delay in etapas:
            self.atualizar_status(texto, valor)
            time.sleep(delay)
            
        # Loop de espera ativa pelo servidor
        tentativas = 0
        while tentativas < 30: # Max 30 segundos
            if verificar_servidor():
                self.atualizar_status("Sistema pronto! Abrindo navegador...", 100)
                time.sleep(0.5)
                webbrowser.open("http://127.0.0.1:5003")
                self.after(1000, self.destroy)
                return
            
            self.atualizar_status(f"Aguardando servidor... ({tentativas}s)", 90 + (tentativas/3))
            time.sleep(1)
            tentativas += 1
            
        self.atualizar_status("Erro ao iniciar servidor!", 100)
        self.after(3000, self.destroy)

    def atualizar_status(self, texto, valor):
        self.status_label.config(text=texto)
        self.progress['value'] = valor
        self.update()

if __name__ == "__main__":
    app = SplashScreen()
    app.mainloop()
