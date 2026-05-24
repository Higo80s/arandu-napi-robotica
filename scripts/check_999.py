from app import app, db
from models import Modalidade, Bolsista, Residente, Edital

with app.app_context():
    mods = Modalidade.query.filter_by(vagas=999).all()
    print(f'Modalidades com 999 vagas: {len(mods)}')
    for m in mods:
        e = Edital.query.get(m.edital_id)
        nb = Bolsista.query.filter_by(modalidade_id=m.id).count()
        nr = Residente.query.filter_by(modalidade_id=m.id).count()
        outras = Modalidade.query.filter(
            Modalidade.edital_id == m.edital_id,
            Modalidade.id != m.id,
            Modalidade.vagas != 999
        ).count()
        print(f'  ID={m.id} nivel={repr(m.nivel)} edital={m.edital_id} num={e.numero if e else "?"} bolsistas={nb} residentes={nr} outras_mods={outras}')
