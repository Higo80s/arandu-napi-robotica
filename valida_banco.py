from app import app, db
from models import Bolsista
from datetime import date

with app.app_context():
    d = date(2026, 2, 1)
    res = Bolsista.query.filter(Bolsista.data_fim_bolsa < d, Bolsista.ativo == True).count()
    print(f"TOTAL_ANTIGAS: {res}")
