"""
Script de Cadastro em Lote - Bolsistas Sucupira V2
Versao com IDs explicitos para evitar problemas de busca.
"""
import sys
sys.path.insert(0, '.')

from app import app
from models import db, Bolsista
from utils import parse_flexible_date

# Mapeamento fixo CAPES DS
# Edital 13 (CAPES): Mod20 Mestrado, Mod21 Doutorado
# Edital 14 (CAPES): Mod22 Mestrado, Mod23 Doutorado
CAPES_MESTRADO = (13, 20)
CAPES_DOUTORADO = (13, 21)

def deactivate_previous_cpf(cpf):
    """Desativa registros ativos com o mesmo CPF."""
    cpf_digits = ''.join(filter(str.isdigit, cpf))
    registros = Bolsista.query.filter(Bolsista.cpf.isnot(None), Bolsista.ativo == True).all()
    count = 0
    for reg in registros:
        if reg.cpf and ''.join(filter(str.isdigit, reg.cpf)) == cpf_digits:
            reg.ativo = False
            reg.motivo_desativacao = "Substituido por novo vinculo (cadastro em lote)"
            count += 1
    return count

def insert(nome, cpf, nivel, data_inicio, data_fim):
    """Insere um novo bolsista."""
    # Determinar edital/modalidade
    if nivel.upper() == 'DOUTORADO':
        edital_id, modalidade_id = CAPES_DOUTORADO
    else:
        edital_id, modalidade_id = CAPES_MESTRADO
    
    # Parse dates
    dt_ini = parse_flexible_date(data_inicio)
    dt_fim = parse_flexible_date(data_fim)
    meses = (dt_fim.year - dt_ini.year) * 12 + (dt_fim.month - dt_ini.month) if dt_ini and dt_fim else 24
    
    # Desativar registros anteriores
    deactivated = deactivate_previous_cpf(cpf)
    if deactivated > 0:
        print(f"    -> {deactivated} registro(s) anterior(es) desativado(s)")
    
    # Criar bolsista
    bolsista = Bolsista(
        nome=nome,
        cpf=cpf,
        edital_id=edital_id,
        modalidade_id=modalidade_id,
        data_inicio_bolsa=dt_ini,
        data_fim_bolsa=dt_fim,
        meses_duracao=meses,
        ativo=True
    )
    db.session.add(bolsista)
    return True

def main():
    with app.app_context():
        print("=" * 60)
        print("CADASTRO EM LOTE - BOLSISTAS SUCUPIRA (V2)")
        print("=" * 60)
        
        # Lista: (nome, cpf, nivel, data_inicio, data_fim)
        bolsistas = [
            ("DEYSE ELEN ALVES PANTOJA", "991.821.492-91", "Doutorado", "01/08/2024", "31/07/2028"),
            ("EDIMARA SALETE DE CARVALHO", "100.389.639-14", "Doutorado", "01/03/2025", "29/02/2028"),
            ("GABRIELLY CRISTINA GALVAO XAVIER", "046.515.409-37", "Doutorado", "01/03/2025", "28/02/2029"),
            ("NAIARA MUCKE", "076.201.989-11", "Doutorado", "01/03/2025", "31/01/2028"),
            ("NATALIE ALANA PEDROSO", "115.066.859-86", "Doutorado", "01/09/2023", "31/01/2027"),
            ("RENATA MICKETEN", "049.287.189-25", "Doutorado", "01/03/2025", "28/02/2029"),
            ("BEATRIZ MASQUETTI PELZ", "045.360.039-59", "Mestrado", "01/07/2024", "28/02/2026"),
            ("JENNIFER VITORIA NOVOSAD NASCIMENTO", "101.095.919-09", "Mestrado", "01/08/2024", "28/02/2026"),
            ("MARIANA GROTTI PEREIRA", "059.964.549-04", "Mestrado", "01/01/2026", "28/02/2027"),
            ("PEDRO IGNACIO DA SILVA MORALES", "096.447.629-08", "Mestrado", "01/01/2026", "31/05/2027"),
            ("YASMIM EMANUELLE MEDEIROS SANSONOVSKI", "100.910.499-38", "Mestrado", "01/09/2025", "31/01/2026"),
        ]
        
        success = 0
        errors = 0
        
        for nome, cpf, nivel, dt_ini, dt_fim in bolsistas:
            print(f"\n[+] {nome}")
            try:
                insert(nome, cpf, nivel, dt_ini, dt_fim)
                success += 1
                print("    [OK]")
            except Exception as e:
                errors += 1
                print(f"    [X] {e}")
        
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"RESUMO: {success} cadastrados, {errors} erros")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERRO CRITICO] Rollback: {e}")

if __name__ == "__main__":
    main()
