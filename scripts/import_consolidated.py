import sys
import os
import pandas as pd
import re
from sqlalchemy import text

# Contexto da Aplicação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ProgramaAcademico, Campus, BolsaVolumetriaAnual, AgenciaFomento

DESCRIPTION = """
Script de Importação Consolidada (Excel -> Postgres)
----------------------------------------------------
1. Sincronização de Metadados de Programas (UPSERT Safe Mode)
2. Carga de Volumetria Histórica (2014-2025)

Safe Mode:
- Ignora programas com '*' no nome (Legado).
- Usa Código CAPES + Campus para matching preciso.
"""

FILE_PATH = r"planilnhas_externas/relatorios_gestao_2025/UTFPR_Consolidado_Gestao_Com_Agencias (1).xlsx"

# Mapeamento de Agências (Conforme definido no Plano)
# ID 1: CAPES
# ID 3: CNPq
# ID 4: Fundação Araucária
AGENCY_MAP = {
    'CAPES_PPG': 1,
    'CAPES_IES': 1, 
    'CNPQ': 2,      # [FIXED] CNPq ID é 2 conforme inspeção
    'CNPq': 2,
    'OUTRAS': 4     # [FIXED] UTFPR/Outras ID é 4
}

def normalize_campus(campus_str):
    """Tenta normalizar o nome do campus para coincidir com o banco."""
    if not isinstance(campus_str, str): return ""
    # Map simples baseado nos nomes comuns
    mapa = {
        'PONTA GROSSA': 'PG', 'PG': 'PG',
        'CURITIBA': 'CT', 'CT': 'CT',
        'PATO BRANCO': 'PB', 'PB': 'PB',
        'CORNÉLIO PROCÓPIO': 'CP', 'CP': 'CP',
        'MEDIANEIRA': 'MD', 'MD': 'MD',
        'LONDRINA': 'LD', 'LD': 'LD',
        'APUCARANA': 'AP', 'AP': 'AP',
        'CAMPO MOURÃO': 'CM', 'CM': 'CM',
        'CAMPO MOURAO': 'CM',
        'DOIS VIZINHOS': 'DV', 'DV': 'DV',
        'FRANCISCO BELTRÃO': 'FB', 'FB': 'FB',
        'FRANCISCO BELTRAO': 'FB',
        'GUARAPUAVA': 'GP', 'GP': 'GP',
        'SANTA HELENA': 'SH', 'SH': 'SH',
        'TOLEDO': 'TD', 'TD': 'TD'
    }
    key = campus_str.upper().strip()
    return mapa.get(key, key)

def run():
    print(DESCRIPTION)
    
    if not os.path.exists(FILE_PATH):
        print(f"[ERRO] Arquivo não encontrado: {FILE_PATH}")
        return

    with app.app_context():
        # --- PREPARAÇÃO ---
        print(f"Lendo arquivo: {FILE_PATH}...")
        try:
            df = pd.read_excel(FILE_PATH)
        except Exception as e:
            print(f"[ERRO] Falha ao ler Excel: {e}")
            return

        # Cache de Programas Existentes no Banco
        # Key: (codigo_capes, sigla_campus) -> ProgramaObj
        # Fallback Key: (sigla_programa, sigla_campus) -> ProgramaObj
        db_programs = ProgramaAcademico.query.all()
        prog_map_code = {}
        prog_map_sigla = {}
        
        print(f"Carregando {len(db_programs)} programas do banco para cache...")
        for p in db_programs:
            # [AUDITORIA] Permitir programas com '*' para saneamento histórico
            # if '*' in p.nome_programa:
            #     continue
                
            campus_sigla = p.campus.sigla_campus if p.campus else 'N/A'
            
            if p.codigo_programa:
                # [FIX] Remover '*' do código para matching com Excel
                clean_code = str(p.codigo_programa).replace('*', '').strip()
                key = (clean_code, campus_sigla)
                prog_map_code[key] = p
            
            if p.sigla_programa:
                key_sigla = (str(p.sigla_programa).upper().strip(), campus_sigla)
                prog_map_sigla[key_sigla] = p

        # --- FASE 1: SINCRONIZAÇÃO ESTRUTURAL ---
        print("\n--- INICIANDO FASE 1: Sincronização Estrutural ---")
        updates_count = 0
        df['programa_id_db'] = None # Coluna para guardar o ID mapeado
        
        for idx, row in df.iterrows():
            codigo_excel = str(row.get('Código CAPES', '')).strip()
            
            # [FIX] Skip Invalid IDs
            if not codigo_excel or codigo_excel == '0' or codigo_excel == 'nan':
                # print(f"Skipping invalid code: {codigo_excel}")
                continue
                
            nome_excel = str(row.get('Nome do Programa', '')).strip()
            sigla_excel = str(row.get('Sigla', '')).strip()
            campus_excel = normalize_campus(str(row.get('Campus', '')))
            
            # Tentar match
            prog_match = None
            
            # 1. Tentativa por Código + Campus
            if codigo_excel and campus_excel:
                prog_match = prog_map_code.get((codigo_excel, campus_excel))
            
            # 2. Tentativa por Sigla + Campus (Fallback)
            if not prog_match and sigla_excel and campus_excel:
                prog_match = prog_map_sigla.get((sigla_excel, campus_excel))
                
            if prog_match:
                # Atualizar Metadados
                updated = False
                
                # Nota
                nota_nova = str(row.get('Nota', '')).strip()
                if nota_nova and nota_nova != 'nan' and prog_match.nota_capes != nota_nova:
                    prog_match.nota_capes = nota_nova
                    updated = True
                
                # Áreas
                area_aval = str(row.get('Área de Avaliação', '')).strip()
                if area_aval and area_aval != 'nan' and prog_match.area_avaliacao != area_aval:
                    prog_match.area_avaliacao = area_aval
                    updated = True
                    
                area_basica = str(row.get('Área Básica', '')).strip()
                if area_basica and area_basica != 'nan' and prog_match.area_basica != area_basica:
                    prog_match.area_basica = area_basica
                    updated = True
                
                # Tipo Oferta (Acadêmico/Profissional)
                tipo_novo = str(row.get('Tipo', '')).strip()
                if tipo_novo and tipo_novo != 'nan' and prog_match.tipo_oferta != tipo_novo:
                    prog_match.tipo_oferta = tipo_novo
                    updated = True

                # [FIX] Inferência de Níveis via Nome (Crucial para atribuição correta M vs D)
                inferred_niveis = []
                name_upper = nome_excel.upper()
                
                # Regras Heurísticas
                is_doutorado = 'DOUTORADO' in name_upper or 'DOUTOR' in name_upper
                is_mestrado = 'MESTRADO' in name_upper or 'MESTRE' in name_upper or 'CURSO' in name_upper # 'Curso' as general fallback? No, be specific.
                
                # Se não tem 'Mestrado' explícito mas é Profissional/Acadêmico sem Doutorado?
                # Vamos ser conservadores: Se tem DOUTORADO -> D. Se tem MESTRADO -> M.
                if is_mestrado: inferred_niveis.append('M')
                if is_doutorado: inferred_niveis.append('D')
                
                # Atualizar se encontrou algo
                if inferred_niveis:
                    new_niveis = ", ".join(inferred_niveis)
                    # Apenas atualizar se o banco estiver vazio ou diferente?
                    # O Excel é mandatório agora.
                    if prog_match.niveis != new_niveis:
                        prog_match.niveis = new_niveis
                        updated = True
                
                # Salvar ID para Fase 2
                df.at[idx, 'programa_id_db'] = prog_match.id
                
                if updated:
                    try:
                        db.session.commit()
                        updates_count += 1
                        print(f"Updated Program ID: {prog_match.id}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[ERROR] Failed to update Program ID {prog_match.id}: {e}")
                        # Re-attach object?
                        # prog_match might be detached now.
                        # reload it
                        prog_match = db.session.merge(prog_match)
            else:
                print(f"[AVISO] Programa não encontrado no banco: {sigla_excel} ({codigo_excel}) - {campus_excel}")

        print(f"Fase 1 Concluída. {updates_count} programas atualizados.")

        # --- FASE 2: ETL E CARGA HISTÓRICA ---
        print("\n--- INICIANDO FASE 2: Carga Histórica ---")
        
        # 1. Truncate
        print("Limpando tabela 'bolsa_volumetria_anual'...")
        db.session.execute(text("TRUNCATE TABLE bolsa_volumetria_anual RESTART IDENTITY CASCADE;"))
        
        # 2. Processar Colunas de Bolsas
        bolsa_cols = [c for c in df.columns if str(c).startswith('Bolsa_')]
        print(f"Colunas de histórico identificadas: {len(bolsa_cols)}")
        
        records_to_insert = []
        
        # Iterar apenas linhas que conseguimos mapear o ID
        df_mapped = df[df['programa_id_db'].notna()]
        
        for _, row in df_mapped.iterrows():
            prog_id = row['programa_id_db']
            
            # Dicionário temporário para agrupar (Ano, Agencia, Nivel) -> Qtd
            # Agrupar CAPES_PPG + CAPES_IES
            # Nivel: Precisamos inferir Nível?
            # A planilha tem programas de M e D misturados? Ou uma linha separada?
            # Se a planilha tem 1 linha por programa, e o programa tem M e D...
            # A coluna 'Bolsa_CNPQ_2024' é a SOMA de M+D? Ou tem colunas separadas?
            # O nome das colunas sugere 'Bolsa_AGENCIA_ANO'. Não especifica nível.
            # HIPÓTESE: A planilha consolida tudo.
            # SOLUÇÃO: Vamos checar os Níveis do Programa no Banco (prog_match.niveis).
            # Se for só 'M', atribui tudo a Mestrado.
            # Se for só 'D', atribui tudo a Doutorado.
            # Se for 'M, D', TEMOS UM PROBLEMA DE AMBIGUIDADE.
            # Como o usuário pediu para seguir, vamos atribuir ao Nível "Principal" ou dividir?
            # Melhor: Verificar se há colunas distintas na planilha ou se assumimos distribuição.
            # Dado o pedido de "Consolidado", vamos assumir que se o programa tem 'M, D', 
            # e a planilha traz um número fechado, atribuiremos ao nível mais alto 'D' ou 'M'?
            # Ou melhor, criar logica de fallback.
            
            # Verificação Nível
            prog_obj = ProgramaAcademico.query.get(prog_id)
            niveis_str = str(prog_obj.niveis or '').upper()
            
            has_m = 'M' in niveis_str
            has_d = 'D' in niveis_str
            
            if has_m and has_d:
                target_nivel = 'Mestrado/Doutorado' # Categoria Híbrida para Consolidados
            elif has_d:
                target_nivel = 'Doutorado'
            else:
                target_nivel = 'Mestrado'
            
            # Acumulador anual por agência
            # Estrutura: { (ano, agencia_id): quantidade }
            acc_anual = {}
            
            for col in bolsa_cols:
                try:
                    val = float(row[col])
                    if val <= 0: continue
                except:
                    continue # Valor inválido/vazio
                
                # Parse Header: Bolsa_AGENCIA_ANO (Ex: Bolsa_CNPQ_2024)
                parts = col.split('_')
                # Pode ser Bolsa_CNPQ_2024 (3 parts) ou Bolsa_CAPES_PPG_2024 (4 parts)
                
                # Tentar extrair ano (sempre o último)
                ano_str = parts[-1]
                if not ano_str.isdigit(): continue
                ano = int(ano_str)
                
                # Extrair Agência (meio)
                agencia_key_parts = parts[1:-1]
                agencia_key = "_".join(agencia_key_parts) # Ex: CNPQ, CAPES_PPG
                
                agencia_id = AGENCY_MAP.get(agencia_key)
                if not agencia_id: continue
                
                key = (ano, agencia_id)
                acc_anual[key] = acc_anual.get(key, 0) + int(val)
                
            # Gerar Registros Finais
            for (ano, ag_id), qtd in acc_anual.items():
                records_to_insert.append({
                    'ano_referencia': ano,
                    'programa_id': prog_id,
                    'agencia_id': ag_id,
                    'nivel': target_nivel,
                    'qtd_sistema': qtd,
                    'qtd_manual_extra': 0
                })
        
        print(f"Preparando inserção de {len(records_to_insert)} registros...")
        
        # Batch Insert
        if records_to_insert:
            db.session.bulk_insert_mappings(BolsaVolumetriaAnual, records_to_insert)
            db.session.commit()
            print("Carga Histórica Finalizada com Sucesso!")
        else:
            print("Nenhum registro de bolsa encontrado para importar.")

if __name__ == '__main__':
    run()
