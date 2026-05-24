from app import app, db, Edital, Residente

with app.app_context():
    # Check Edital 21
    edital_21 = Edital.query.filter_by(numero='21').first()
    if edital_21:
        print(f"✅ Edital 21 found: ID {edital_21.id} - {edital_21.descricao}")
    else:
        print("❌ Edital 21 NOT FOUND.")

    # Check Inconsistent Residents
    inconsistent = Residente.query.filter(Residente.recebe_bolsa == True, Residente.edital_id == None).all()
    if inconsistent:
        print(f"❌ Found {len(inconsistent)} residents with scholarship but NO Edital link:")
        for r in inconsistent:
            print(f"   - ID {r.id}: {r.nome} (CPF: {r.cpf})")
    else:
        print("✅ No inconsistent residents found (All scholars are linked).")
