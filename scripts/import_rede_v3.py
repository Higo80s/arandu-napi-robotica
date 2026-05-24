import csv
import sys
import os

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import AgenciaFomento, BolsaVolumetriaAnual, ProgramaAcademico, Campus

def get_agencia_rede():
    agencia = AgenciaFomento.query.filter_by(sigla='CAPES').first()
    return agencia

def get_campus_map():
    return {c.sigla_campus: c.id for c in Campus.query.all()}

def import_csv_rede_multicampi(file_path, nivel_default='Mestrado'):
    print(f"\n--- Iniciando Importação REDE (Multi-Campi): {file_path} ---")
    
    agencia = get_agencia_rede()
    if not agencia:
        print("ERRO: Agência CAPES não encontrada.")
        return

    campi_map = get_campus_map()
    
    # Cache de Programas: (Sigla, CampusID) -> ProgramaObj
    # Isso resolve a ambiguidade de PROFMAT-CT vs PROFMAT-PB
    programas_cache = {}
    todos_progs = ProgramaAcademico.query.all()
    
    for p in todos_progs:
        key = (p.sigla_programa, p.campus_id)
        programas_cache[key] = p
        
    stats = {} # (Ano, ProgID, AgenciaID) -> Quantidade

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            prog_sigla = row['Programa'].strip()
            campus_sigla = row['Campus'].strip()
            
            # Mapas manuais de Sigla CSV -> Sigla Banco se necessário
            if prog_sigla == 'PROFIAGUA': prog_sigla = 'PROFÁGUA'
            
            # Resolver Campus ID
            campus_id = campi_map.get(campus_sigla)
            if not campus_id:
                print(f"ERRO: Campus '{campus_sigla}' não encontrado. Pulando linha.")
                continue
                
            # Resolver Programa (Sigla + Campus)
            programa = programas_cache.get((prog_sigla, campus_id))
            
            if not programa:
                # Tenta fallback sem case sensitivity?
                # Por enquanto apenas loga
                print(f"ERRO: Programa '{prog_sigla}' no campus '{campus_sigla}' não encontrado. Verifique se o programa existe neste campus.")
                continue
            
            # Iterar anos
            for ano in range(2014, 2026):
                col_ano = str(ano)
                if col_ano in row:
                    qtd_str = row[col_ano].strip()
                    qtd = int(qtd_str) if qtd_str.isdigit() else 0
                    # if qtd > 0: # REMOVIDO para permitir zerar
                    key = (ano, programa.id, agencia.id)
                    stats[key] = stats.get(key, 0) + qtd

    print(f"Dados processados. {len(stats)} chaves de volumetria identificadas.")
    
    count_inserts = 0
    count_updates = 0
    
    for key, qtd_total in stats.items():
        ano, prog_id, ag_id = key
        
        volumetria = BolsaVolumetriaAnual.query.filter_by(
            ano_referencia=ano,
            programa_id=prog_id,
            agencia_id=ag_id,
            nivel=nivel_default
        ).first()
        
        if volumetria:
            if volumetria.qtd_sistema != qtd_total:
                print(f"Update {ano} ProgID {prog_id}: {volumetria.qtd_sistema} -> {qtd_total}")
                volumetria.qtd_sistema = qtd_total
                count_updates += 1
        else:
            print(f"Insert {ano} ProgID {prog_id}: {qtd_total}")
            volumetria = BolsaVolumetriaAnual(
                ano_referencia=ano,
                programa_id=prog_id,
                agencia_id=ag_id,
                nivel=nivel_default,
                qtd_sistema=qtd_total,
                qtd_manual_extra=0
            )
            db.session.add(volumetria)
            count_inserts += 1
            
    db.session.commit()
    print(f"Concluído! Inseridos: {count_inserts}, Atualizados: {count_updates}")

def run():
    csv_rede = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas\bolsas_rede_2014_2025.csv"
    with app.app_context():
        import_csv_rede_multicampi(csv_rede, nivel_default='Mestrado')

if __name__ == '__main__':
    run()
