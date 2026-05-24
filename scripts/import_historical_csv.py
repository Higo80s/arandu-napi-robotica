import csv
import sys
import os

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import AgenciaFomento, BolsaVolumetriaAnual, ProgramaAcademico, Campus

def get_agencia_rede():
    # Programas em Rede geralmente são CAPES ou CAPES + IES. 
    # O user disse "Fonte: DIRPPGs, PROPPG e capes_ppg".
    # Vamos assumir CAPES como padrão ou criar uma lógica específica se tiver detalhe.
    # No CSV de rede não tem coluna Agência, vamos assumir CAPES.
    agencia = AgenciaFomento.query.filter_by(sigla='CAPES').first()
    return agencia

def import_csv_rede(file_path, nivel_default='Mestrado'):
    print(f"\n--- Iniciando Importação REDE: {file_path} ([{nivel_default}]) ---")
    
    agencia = get_agencia_rede()
    if not agencia:
        print("ERRO: Agência CAPES não encontrada.")
        return

    # Mapeamento de Programas (Sigla -> ID)
    progs_db = {p.sigla_programa: p for p in ProgramaAcademico.query.all()}
    
    # Mapeamento de Campus (Sigla -> ID) para logs ou verificação se necessário
    # O CSV de Rede tem coluna 'Campus' (CT, PB, CP, etc)
    # Mas a tabela BolsaVolumetriaAnual liga Programa -> Campus.
    # O Programa PROFMAT existe em vários campi? 
    # Se 'PROFMAT' for um único registro na tabela ProgramaAcademico, temos um problema,
    # pois a volumetria é por programa.
    # Se houver um 'PROFMAT' para cada campus (PROFMAT-CT, PROFMAT-PB), ok.
    # Caso contrário, vamos somar tudo no 'PROFMAT' único ou teremos que criar programas específicos?
    # Vamos checar como está no banco.
    
    stats = {} # (Ano, ProgID, AgenciaID) -> Quantidade

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            programa_sigla = row['Programa'].strip()
            # O código parece ser o código CAPES/Sucupira
            
            # Tenta achar o programa
            programa = progs_db.get(programa_sigla)
            
            # TENTATIVA DE RESOLUÇÃO MULTICAMPI
            # Se não achou 'PROFMAT', tenta 'PROFMAT-CT' (exemplo hipotético)
            # Ou se o user mandou separado por campus, mas o banco só tem um geral.
            
            if not programa:
                print(f"AVISO: Programa de Rede '{programa_sigla}' não encontrado no banco. Pulando.")
                continue
            
            # Iterar colunas de anos (2014 a 2025)
            for ano in range(2014, 2026):
                col_ano = str(ano)
                if col_ano in row:
                    qtd = int(row[col_ano]) if row[col_ano].isdigit() else 0
                    if qtd > 0:
                        key = (ano, programa.id, agencia.id)
                        stats[key] = stats.get(key, 0) + qtd

    print(f"Dados de REDE processados. Gravando no banco ({len(stats)} registros)...")
    
    count_inserted = 0
    count_updated = 0
    
    for key, qtd_total in stats.items():
        ano, prog_id, ag_id = key
        
        # Busca registro existente (pode ter vindo do outro CSV ou ser update)
        # IMPORTANTE: Programas de REDE não deveriam estar no outro CSV segundo o user.
        # Então é insert ou update se rodar 2x.
        
        volumetria = BolsaVolumetriaAnual.query.filter_by(
            ano_referencia=ano,
            programa_id=prog_id,
            agencia_id=ag_id,
            nivel=nivel_default
        ).first()
        
        if volumetria:
            # SOMA ou SUBSTITUI?
            # Se o programa aparece em ambos os arquivos (erro do user?), somar seria o correto?
            # Mas o script anterior substitui. 
            # Vamos assumir que Rede é disjunto.
            # Se já tem valor, e é de rede, atualizamos.
            if volumetria.qtd_sistema != qtd_total:
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

def import_csv_regular(file_path, nivel_default='Mestrado'):
    print(f"\n--- Iniciando Importação REGULAR: {file_path} ([{nivel_default}]) ---")
    
    agencias_db = {a.sigla: a for a in AgenciaFomento.query.all()}
    progs_db = {p.sigla_programa: p for p in ProgramaAcademico.query.all()}
    
    def resolve_agencia(csv_agencia):
        csv_agencia = csv_agencia.lower().strip().replace('"', '')
        if 'capes' in csv_agencia: return agencias_db.get('CAPES')
        elif 'cnpq' in csv_agencia: return agencias_db.get('CNPq')
        elif 'araucária' in csv_agencia or 'araucaria' in csv_agencia: return agencias_db.get('Fundação Araucária')
        elif 'utfpr' in csv_agencia or 'próprio' in csv_agencia: return agencias_db.get('UTFPR')
        return agencias_db.get('Outras')

    stats = {} 

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sigla = row['Sigla'].strip()
            if not row['Ano'] or not row['Quantidade']: continue
            
            ano = int(row['Ano'])
            qtd = int(row['Quantidade'])
            agencia_raw = row['Agencia']
            
            programa = progs_db.get(sigla)
            if not programa: continue
                
            agencia = resolve_agencia(agencia_raw)
            if not agencia: continue
            
            key = (ano, programa.id, agencia.id)
            stats[key] = stats.get(key, 0) + qtd

    print(f"Dados REGULARES processados. Gravando...")
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
    print(f"Regular Concluído! Inseridos: {count_inserted}, Atualizados: {count_updated}")

def run():
    base_path = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\planilnhas_externas"
    csv_regular = os.path.join(base_path, "dados_bolsas_utfpr_normalizado_2014_2025.csv")
    csv_rede = os.path.join(base_path, "bolsas_rede_2014_2025.csv")
    
    with app.app_context():
        # 1. Importar Regular
        if os.path.exists(csv_regular):
            import_csv_regular(csv_regular, nivel_default='Mestrado')
        
        # 2. Importar Rede (Aditivo)
        if os.path.exists(csv_rede):
            import_csv_rede(csv_rede, nivel_default='Mestrado')

if __name__ == '__main__':
    run()
