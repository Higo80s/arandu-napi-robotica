
from app import app, db
from models import Residente, Edital, Modalidade

def run():
    with app.app_context():
        print("--- Detaching Residents from Editais ---")
        
        # 1. Unlink Residents from Editais
        # Set edital_id = NULL for all residents
        residents = Residente.query.all()
        count_unlink = 0
        for r in residents:
            if r.edital_id is not None:
                r.edital_id = None
                r.modalidade_id = None # Also decouple modality as it is linked to Edital
                count_unlink += 1
        
        db.session.commit()
        print(f"✅ Unlinked {count_unlink} residents from Editais.")

        # 2. Delete "Residência Pós-Doutoral" Edital(s)
        # Find by name/description
        target_name = "Residência Pós-Doutoral"
        editais = Edital.query.filter(Edital.numero.ilike(f'%{target_name}%')).all()
        
        # Also check description
        editais_desc = Edital.query.filter(Edital.descricao.ilike(f'%{target_name}%')).all()
        
        # Unique list
        all_targets = list(set(editais + editais_desc))
        
        if not all_targets:
            print(f"⚠️  No Edital found with name '{target_name}'.")
        else:
            for e in all_targets:
                print(f"DTO: Deleting Edital {e.id} - {e.numero} ({e.descricao})")
                db.session.delete(e)
            
            db.session.commit()
            print(f"✅ Deleted {len(all_targets)} Edital(s).")
            
        print("--- Done ---")

if __name__ == '__main__':
    run()
