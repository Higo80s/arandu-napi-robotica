from app import app, db
from models import Bolsista, Acompanhamento, Afastamento

def verify():
    with app.app_context():
        print("1. Querying Bolsista...")
        b = Bolsista.query.first()
        if b:
            print(f"   Found bolsista: {b.id}")
            print("2. Accessing Acompanhamentos...")
            # Check if relationship works
            ac = b.acompanhamentos
            print(f"   Acompanhamentos count: {len(ac)}")
            
            print("3. Accessing Afastamentos...")
            af = b.afastamentos
            print(f"   Afastamentos count: {len(af)}")
            
            print("4. Accessing Programa Link...")
            if b.programa_link:
                print(f"   Programa: {b.programa_link.nome_programa}")
            else:
                print("   No Programa Link")
                
            print("5. Accessing Edital/Modalidade...")
            print(f"   Edital: {b.edital.numero}")
            print(f"   Modalidade: {b.modalidade.nivel}")
        else:
            print("   No bolsistas found (empty db?), but query worked.")
        
        print("Verification Successful!")

if __name__ == "__main__":
    verify()
