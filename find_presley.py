
from app import app
from models import db, Bolsista, Residente, Candidatura
import time

def find_presley():
    cpf_alvo = '107.796.884-14'
    print(f"🔍 Buscando registros para o CPF: {cpf_alvo}")
    
    with app.app_context():
        # Busca em Bolsistas
        bolsistas = Bolsista.query.all()
        found_b = []
        for b in bolsistas:
            if b.cpf:
                try:
                    dec_cpf = b.cpf.strip()
                    if dec_cpf == cpf_alvo:
                        found_b.append({
                            'id': b.id,
                            'nome': b.nome,
                            'ativo': b.ativo,
                            'cpf_banco': b.cpf,
                            'tipo': 'Bolsista'
                        })
                except:
                    continue
        
        # Busca em Residentes
        residentes = Residente.query.all()
        found_r = []
        for r in residentes:
            if r.cpf and r.cpf.strip() == cpf_alvo:
                found_r.append({
                    'id': r.id,
                    'nome': r.nome,
                    'ativo': getattr(r, 'ativo', 'N/A'),
                    'tipo': 'Residente'
                })
        
        # Busca em Candidaturas
        candidaturas = Candidatura.query.all()
        found_c = []
        for c in candidaturas:
            if c.cpf and c.cpf.strip() == cpf_alvo:
                found_c.append({
                    'id': c.id,
                    'nome': c.nome,
                    'status': c.status,
                    'rodada': c.rodada_id
                })

        print("\n--- Resultados em Bolsistas ---")
        for f in found_b: print(f)
        
        print("\n--- Resultados em Residentes ---")
        for f in found_r: print(f)
        
        print("\n--- Resultados em Candidaturas ---")
        for f in found_c: print(f)

if __name__ == "__main__":
    find_presley()
