import csv
import sys
import os

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import AgenciaFomento, BolsaVolumetriaAnual, ProgramaAcademico

def get_agencia_rede():
    agencia = AgenciaFomento.query.filter_by(sigla='CAPES').first()
    return agencia

def import_csv_rede(file_path, nivel_default='Mestrado'):
    print(f"\n--- Iniciando Importação REDE (Códigos Exatos): {file_path} ([{nivel_default}]) ---")
    
    agencia = get_agencia_rede()
    if not agencia:
        print("ERRO: Agência CAPES não encontrada.")
        return

    # Mapeamento: "Sigla do CSV" -> "Sigla no Banco"
    # Ajuste manual baseado na saída do script list_programs.py e no CSV do usuário
    mapa_siglas = {
        'PROFMAT': 'PROFMAT',
        'PROFIS': 'PROFIS',
        'PROFIAGUA': 'ProfÁgua', # Suposição comum
        'PROFQUI': 'PROFQUI',
        'PROFIAP': 'PROFIAP',
        'PROFNIT': 'PROFNIT'
    }
    
    # Busca objeto Programa no banco
    progs_db = {}
    todos_progs = ProgramaAcademico.query.all()
    
    # 1. Mapa direto por sigla
    for p in todos_progs:
        progs_db[p.sigla_programa] = p
        
    stats = {} # (Ano, ProgID, AgenciaID) -> Quantidade

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            programa_csv = row['Programa'].strip()
            
            # Tenta resolver a sigla do banco
            sigla_banco = mapa_siglas.get(programa_csv, programa_csv)
            
            # Tenta achar o programa no banco
            programa = progs_db.get(sigla_banco)
            
            # Fallback: Tenta achar 'parecido' (case insensitive ou contains)
            if not programa:
                for p in todos_progs:
                    if programa_csv.lower() in p.nome_programa.lower() or programa_csv.lower() in p.sigla_programa.lower():
                        print(f"INFO: Mapeando '{programa_csv}' -> '{p.sigla_programa}' ({p.nome_programa})")
                        programa = p
                        break
            
            if not programa:
                print(f"ERRO: Programa de Rede '{programa_csv}' não encontrado no banco de dados. Pulando.")
                continue
            
            # Iterar colunas de anos (2014 a 2025)
            for ano in range(2014, 2026):
                col_ano = str(ano)
                if col_ano in row:
                    qtd_str = row[col_ano].strip()
                    qtd = int(qtd_str) if qtd_str.isdigit() else 0
                    if qtd > 0:
                        key = (ano, programa.id, agencia.id)
                        stats[key] = stats.get(key, 0) + qtd

    print(f"Dados de REDE processados. Gravando no banco ({len(stats)} registros)...")
    
    count_inserted = 0
    count_updated = 0
    
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
                print(f"Atualizando {ano} Prog {prog_id}: {volumetria.qtd_sistema} -> {qtd_total}")
                volumetria.qtd_sistema = qtd_total
                count_updated += 1
        else:
            volumetria = BolsaVolumetriaAnual(
                ano_referencia=ano,
                programa_id=prog_id,
                agencia_id=ag_id,
                nivel=nivel_default,
                qtd_sistema=qtd_total,
                qtd_manual_extra=0
            )
            db.session.add(volumetria)
            count_inserted += 1
            
    db.session.commit()
    print(f"Rede Concluída! Inseridos: {count_inserted}, Atualizados: {count_updated}")

def run():
    csv_rede = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas\bolsas_rede_2014_2025.csv"
    with app.app_context():
        import_csv_rede(csv_rede, nivel_default='Mestrado')

if __name__ == '__main__':
    run()
