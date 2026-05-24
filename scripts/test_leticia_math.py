import sys
sys.path.append('.')
from app import app
from models import Bolsista
from datetime import date
from dateutil.relativedelta import relativedelta

with app.app_context():
    b = Bolsista.query.filter(Bolsista.nome.ilike('%Letícia Bito Maynart%')).first()
    if b:
        qtd_parcelas_pagas = len(b.acompanhamentos)
        print(f"Bolsista: {b.nome}, Acompanhamentos: {qtd_parcelas_pagas}, data_inicio: {b.data_inicio_bolsa}, data_fim: {b.data_fim_bolsa}, meses_duracao: {b.meses_duracao}")
        
        hoje_proj = date.today() + relativedelta(months=1)
        print(f"hoje_proj (date.today() + 1 month): {hoje_proj}")
        cutoff = min(hoje_proj, b.data_fim_bolsa)
        print(f"cutoff: {cutoff}")
        
        if cutoff > b.data_inicio_bolsa:
            diff = relativedelta(cutoff, b.data_inicio_bolsa)
            qtd_parcelas_pagas = diff.years * 12 + diff.months
            print(f"diff: {diff.years} years, {diff.months} months, {diff.days} days")
            print(f"qtd_parcelas_pagas calculated via relativedelta: {qtd_parcelas_pagas}")
        
        # Test math logic
        qtd_math = (cutoff.year - b.data_inicio_bolsa.year) * 12 + (cutoff.month - b.data_inicio_bolsa.month)
        print(f"qtd_parcelas_pagas calculated via calendar math: {qtd_math}")
