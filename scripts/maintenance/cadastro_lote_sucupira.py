"""
Script de Cadastro em Lote - Bolsistas Sucupira
Atualização V16: Suporte a múltiplos vínculos por CPF
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Bolsista, Edital, Modalidade, ProgramaAcademico
from datetime import date
from utils import parse_flexible_date

def find_programa(cod_sucupira):
    """Busca programa pelo código Sucupira."""
    prog = ProgramaAcademico.query.filter_by(codigo_programa=cod_sucupira).first()
    return prog.id if prog else None

def find_edital_modalidade(agencia_keyword, nivel):
    """
    Busca edital e modalidade por nome da agência e nível.
    Ex: agencia_keyword='DS' ou 'CAPES' ou 'Recursos'
    """
    for edital in Edital.query.all():
        if agencia_keyword.upper() in edital.agencia.upper():
            for mod in edital.modalidades:
                if mod.nivel.upper() == nivel.upper():
                    return edital.id, mod.id
    return None, None

def deactivate_previous_cpf(cpf_digits):
    """Desativa registros ativos com o mesmo CPF."""
    registros = Bolsista.query.filter(Bolsista.cpf.isnot(None), Bolsista.ativo == True).all()
    count = 0
    for reg in registros:
        if reg.cpf and ''.join(filter(str.isdigit, reg.cpf)) == cpf_digits:
            reg.ativo = False
            reg.motivo_desativacao = f"Substituído por novo vínculo (cadastro em lote)"
            count += 1
    return count

def insert_bolsista(nome, cpf, cod_programa, nivel, data_inicio, data_fim, edital_keyword):
    """Insere um novo bolsista com auto-desativação de registros anteriores."""
    cpf_digits = ''.join(filter(str.isdigit, cpf))
    
    # Buscar edital e modalidade
    edital_id, modalidade_id = find_edital_modalidade(edital_keyword, nivel)
    if not edital_id:
        print(f"[ERRO] Edital/Modalidade não encontrado: {edital_keyword}/{nivel} para {nome}")
        return False
    
    # Buscar programa
    programa_id = find_programa(cod_programa)
    if not programa_id:
        print(f"[AVISO] Programa não encontrado: {cod_programa} para {nome}. Cadastrando sem programa.")
    
    # Desativar registros anteriores
    deactivated = deactivate_previous_cpf(cpf_digits)
    if deactivated > 0:
        print(f"  -> {deactivated} registro(s) anterior(es) desativado(s) para CPF {cpf}")
    
    # Calcular meses de duracao
    dt_ini = parse_flexible_date(data_inicio)
    dt_fim = parse_flexible_date(data_fim)
    if dt_ini and dt_fim:
        meses = (dt_fim.year - dt_ini.year) * 12 + (dt_fim.month - dt_ini.month)
    else:
        meses = 24  # Default fallback
    
    # Criar novo bolsista
    bolsista = Bolsista(
        nome=nome,
        cpf=cpf,
        edital_id=edital_id,
        modalidade_id=modalidade_id,
        programa_id=programa_id,
        data_inicio_bolsa=dt_ini,
        data_fim_bolsa=dt_fim,
        data_inicio_curso=dt_ini,
        previsao_defesa=dt_fim,
        meses_duracao=meses,
        ativo=True
    )
    
    db.session.add(bolsista)
    return True

def main():
    with app.app_context():
        print("=" * 60)
        print("CADASTRO EM LOTE - BOLSISTAS SUCUPIRA")
        print("=" * 60)
        
        # Lista de bolsistas a cadastrar
        # Formato: (nome, cpf, cod_programa, nivel, data_inicio, data_fim, edital_keyword)
        bolsistas = [
            # Caso 1: DEYSE - Mestrado -> Doutorado
            ("DEYSE ELEN ALVES PANTOJA", "991.821.492-91", "40006018013P0", "Doutorado", "01/08/2024", "31/07/2028", "CAPES"),
            
            # Caso 2: EDIMARA - Novo cadastro
            ("EDIMARA SALETE DE CARVALHO", "100.389.639-14", "40006018176P6", "Doutorado", "01/03/2025", "29/02/2028", "CAPES"),
            
            # Caso 3: GABRIELLY - Mestrado -> Doutorado  
            ("GABRIELLY CRISTINA GALVAO XAVIER", "046.515.409-37", "40006018176P6", "Doutorado", "01/03/2025", "28/02/2029", "CAPES"),
            
            # Caso 4: NAIARA - Mudança de edital (para CAPES DS)
            ("NAIARA MUCKE", "076.201.989-11", "40006018016P9", "Doutorado", "01/03/2025", "31/01/2028", "CAPES"),
            
            # Caso 5: NATALIE - Mudança de edital (para CAPES DS)
            ("NATALIE ALANA PEDROSO", "115.066.859-86", "40006018181P0", "Doutorado", "01/09/2023", "31/01/2027", "CAPES"),
            
            # Caso 6: RENATA - Mestrado -> Doutorado
            ("RENATA MICKETEN", "049.287.189-25", "40006018176P6", "Doutorado", "01/03/2025", "28/02/2029", "CAPES"),
            
            # Caso 7: ALBERICO - JÁ ATUALIZADO MANUALMENTE - PULADO
            
            # Caso 8: BEATRIZ - Mudança de edital (para CAPES DS)
            ("BEATRIZ MASQUETTI PELZ", "045.360.039-59", "40006018012P3", "Mestrado", "01/07/2024", "28/02/2026", "CAPES"),
            
            # Caso 9: JENNIFER - Mudança de edital (para CAPES DS)
            ("JENNIFER VITORIA NOVOSAD NASCIMENTO", "101.095.919-09", "40006018177P2", "Mestrado", "01/08/2024", "28/02/2026", "CAPES"),
            
            # Caso 10: MARIANA - Novo cadastro
            ("MARIANA GROTTI PEREIRA", "059.964.549-04", "40006018023P5", "Mestrado", "01/01/2026", "28/02/2027", "CAPES"),
            
            # Caso 11: PEDRO - Novo cadastro
            ("PEDRO IGNACIO DA SILVA MORALES", "096.447.629-08", "40006018003P4", "Mestrado", "01/01/2026", "31/05/2027", "CAPES"),
            
            # Caso 12: YASMIM - Mudança de edital (para CAPES DS)
            ("YASMIM EMANUELLE MEDEIROS SANSONOVSKI", "100.910.499-38", "40006018176P6", "Mestrado", "01/09/2025", "31/01/2026", "CAPES"),
        ]
        
        success_count = 0
        error_count = 0
        
        for nome, cpf, cod_programa, nivel, dt_ini, dt_fim, edital in bolsistas:
            print(f"\n[+] Cadastrando: {nome}")
            try:
                if insert_bolsista(nome, cpf, cod_programa, nivel, dt_ini, dt_fim, edital):
                    success_count += 1
                    print(f"    [OK] Sucesso!")
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"    [X] Erro: {e}")
        
        # Commit final
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"RESUMO: {success_count} cadastrados, {error_count} erros")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERRO CRÍTICO] Rollback executado: {e}")

if __name__ == "__main__":
    main()
