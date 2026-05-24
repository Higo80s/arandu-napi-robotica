import sys
import os
from datetime import date
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Bolsista

with app.app_context():
    hoje = date(2026, 3, 1) # Assumindo 1 de março 
    
    # Simula a query feita em app.py -> alertas_index()
    alert_bolsistas = Bolsista.query.filter(
        Bolsista.data_fim_bolsa < hoje,
        db.or_(Bolsista.ativo == True, Bolsista.motivo_desligamento == 'Finalizando')
    ).order_by(Bolsista.data_fim_bolsa.asc()).all()
    
    # 126 devem aparecer aqui (os de fev q marcamos com finalizando)
    # + eventuais q venceram tb em dias de mar (ou fev q estavam ativos e n eram dos 126, apesar q limpamos < 01/02)
    print(f"Bolsistas listados no alerta: {len(alert_bolsistas)}")
    
    for b in alert_bolsistas[:10]:
        print(f"{b.nome} - Fim: {b.data_fim_bolsa} | Motivo: {b.motivo_desligamento}")
