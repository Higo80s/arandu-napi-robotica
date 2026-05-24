"""
MOTOR DE SINCRONIZAÇÃO ACADÊMICA (v10.9)
=========================================

Implementa o Strategy Pattern para sincronizar dados de diferentes fontes
com a base de bolsistas do Arandú via UPSERT por CPF.

Hierarquia de Importação:
1. Sistema Acadêmico (UTFPR) → Fonte de IDENTIDADE (Matrícula, E-mail @alunos)
2. CAPES/SCBA                → Fonte de ENRIQUECIMENTO (Vigência, Fomento)
"""

import csv
import io
import logging
import hashlib
from datetime import datetime
from typing import Protocol, List, Dict, Any

from extensions import db
from models import Bolsista, DatabaseMemento
from core.memento import BolsistaCaretaker

logger = logging.getLogger(__name__)


# ============================================================================
# PROTOCOLO BASE (Strategy Interface)
# ============================================================================

class DataParser(Protocol):
    """Interface para todos os parsers de fontes de dados."""
    source_name: str

    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        """Transforma dados brutos em lista de dicionários normalizados."""
        ...

    def get_key_field(self) -> str:
        """Retorna o campo usado como chave de deduplicação (ex: 'cpf')."""
        ...


# ============================================================================
# DICIONÁRIO DE TRADUÇÃO (Regras de Negócio)
# ============================================================================

TRANSLATION_MAP = {
    # Mapeamento Fonte → Agência de Fomento (para agencia_fomento)
    "CAPES-DS": "CAPES",
    "CAPES-PDSE": "CAPES",
    "CAPES-GCUB": "CAPES/GCUB",
    "CNPq-PQ": "CNPq",
    "FA-NAPI": "Fundação Araucária",
    # Mapeamento Nível → Modal do Sistema
    "ME": "Mestrado",
    "DO": "Doutorado",
    "PD": "Pós-Doutorado",
}

# ============================================================================
# PARSERS CONCRETOS (Strategies)
# ============================================================================

class AcademicParser:
    """
    [V10.9] Parser para relatório do sistema acadêmico da UTFPR.
    Arquivo: Alunos_bolsistas_todos_fevereiro_2026.csv

    Formato Real (auditado em 12/03/2026):
    - Delimitador: ;
    - Encoding: latin-1
    - Colunas: " ""NomeCol"" " (aspas duplas encadeadas com espaço)
    - Valores: " ""Dado"" " (mesmo padrão nas células)

    Colunas do relatório (índice 0-based):
    0:Seq.  1:Câmpus  2:Programa  3:Código(matrícula)  4-5:flags
    6:Nome  7:Data Ingresso  8:Situação  9:Data Defesa  10:Data Lançamento
    11:CPF  12:Data Nasc.  13:Sexo  14:Fonte  15:Data Início  16:Data Fim
    17:Inativar  18:Email
    """
    source_name = "SistemaAcademicoUTFPR"

    def parse(self, raw_data: str) -> list:
        """
        Lê o CSV acadêmico UTFPR e normaliza os dados.

        Formato confirmado (auditado 12/03/2026):
        - Encoding: UTF-8 (arquivo exportado do sistema UTFPR)
        - Delimitador: ;
        - Colunas/Valores com aspas duplas encadeadas: ' ""Valor"" '
        - Colunas (posição fixa):
          [03] Código = RA/Matrícula  [11] CPF
          [06] Nome   [09] Data Defesa  [18] Email
        """
        import re
        try:
            import pandas as pd
        except ImportError:
            logger.error("[AcademicParser] pandas não instalado. Execute: pip install pandas")
            return []

        try:
            import io as _io

            # 1. Ler com UTF-8 e delimitador ;
            df = pd.read_csv(
                _io.StringIO(raw_data),
                sep=';',
                encoding_errors='replace',  # fallback seguro para byte inválido ocasional
                dtype=str,
                on_bad_lines='skip'
            )

            # 2. Limpar nomes das colunas: remove todas as aspas e espaços residuais
            df.columns = [c.replace('"', '').strip() for c in df.columns]

            # 3. Limpar dados de todas as células: mesma limpeza simples
            for col in df.columns:
                df[col] = df[col].astype(str).str.replace('"', '').str.strip()

            logger.info(f"[AcademicParser] Colunas: {df.columns.tolist()}")

            # 4. Localizar colunas pelo nome (UTF-8 preserva acentos)
            cols = list(df.columns)

            def find_by_name(*keywords):
                """Busca case-insensitive por substring no nome da coluna."""
                for kw in keywords:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return col
                return None

            def find_by_pos(idx):
                return cols[idx] if idx < len(cols) else None

            # Com UTF-8, 'Código' aparece corretamente; posição [3] = fallback
            col_cpf    = find_by_name('cpf')                              or find_by_pos(11)
            col_mat    = find_by_name('código', 'codigo', 'ódigo', 'digo') or find_by_pos(3)
            col_nome   = find_by_name('nome')                              or find_by_pos(6)
            col_email  = find_by_name('email')                             or find_by_pos(18)
            col_defesa = find_by_name('defesa')                            or find_by_pos(9)
            # [NEW V10.9] Mapeamento expandido
            col_campus    = find_by_name('mpus', 'campus')                 or find_by_pos(1)
            col_programa  = find_by_name('programa')                       or find_by_pos(2)
            col_ingresso  = find_by_name('ingresso')                       or find_by_pos(7)
            col_situacao  = find_by_name('ituação', 'ituacao', 'situa')   or find_by_pos(8)
            col_sexo      = find_by_name('sexo')                           or find_by_pos(13)
            col_datafim   = find_by_name('data fim', 'fim')               or find_by_pos(16)

            logger.info(
                f"[AcademicParser] CPF={col_cpf} | RA={col_mat} | "
                f"Nome={col_nome} | Email={col_email} | Defesa={col_defesa}"
            )

            if not col_cpf:
                logger.error("[AcademicParser] Coluna CPF não encontrada no CSV.")
                return []

            # 5. Filtrar somente linhas com CPF de 11 dígitos numéricos
            df = df[df[col_cpf].str.replace(r'\D', '', regex=True).str.len() == 11]

            records = []
            for _, row in df.iterrows():
                cpf = re.sub(r'\D', '', str(row.get(col_cpf, '')))
                if len(cpf) != 11:
                    continue

                mat = str(row.get(col_mat, '')).strip()
                # Válido apenas se for numérico (descarta 'PPGEQ-AP', 'nan', etc.)
                if not re.match(r'^\d{5,10}$', mat):
                    mat = ''

                records.append({
                    "cpf":             cpf,
                    "matricula":       mat,
                    "nome":            str(row.get(col_nome, '')).strip() if col_nome else '',
                    "email_academico": str(row.get(col_email, '')).strip() if col_email else '',
                    "data_defesa_str": str(row.get(col_defesa, '')).strip() if col_defesa else '',
                    # [NEW V10.9] campos expandidos
                    "campus":          str(row.get(col_campus, '')).strip() if col_campus else '',
                    "programa_sigla":  str(row.get(col_programa, '')).strip() if col_programa else '',
                    "data_ingresso":   str(row.get(col_ingresso, '')).strip() if col_ingresso else '',
                    "situacao":        str(row.get(col_situacao, '')).strip() if col_situacao else '',
                    "sexo":            str(row.get(col_sexo, '')).strip() if col_sexo else '',
                    "data_fim_csv":    str(row.get(col_datafim, '')).strip() if col_datafim else '',
                    "_source":         self.source_name,
                })

            logger.info(f"[AcademicParser] {len(records)} registros extraídos.")
            return records

        except Exception as e:
            logger.error(f"[AcademicParser] Erro fatal ao parsear CSV: {e}")
            return []

    def get_key_field(self) -> str:
        return "cpf"


# ============================================================================
# MOTOR DE SINCRONIZAÇÃO PRINCIPAL
# ============================================================================

class SyncEngine:
    """
    [V10.9] Orquestra a sincronização de dados usando o Strategy Pattern.
    
    Fluxo:
    1. Cria snapshot (Memento) antes de qualquer modificação.
    2. Processa cada registro do parser.
    3. Executa UPSERT: se CPF existe → atualiza; se não → cria.
    4. Gera relatório de batimento.
    """

    def __init__(self, parser: DataParser):
        self.parser = parser
        self.caretaker = BolsistaCaretaker()
        self._report = {"matched": 0, "created": 0, "skipped": 0, "errors": []}

    def _build_cpf_index(self) -> dict:
        """
        [V10.9] Constrói um índice {cpf_texto_plano: bolsista} carregando
        todos os registros. Necessário porque o CPF usa Fernet (IV aleatório),
        então filter_by(cpf=X) nunca funciona via SQL — o match precisa ser
        feito em Python após descriptografia automática pelo SQLAlchemy.
        """
        import re
        index = {}
        todos = Bolsista.query.all()
        logger.info(f"[SyncEngine] Construindo índice de {len(todos)} bolsistas...")
        for b in todos:
            cpf_raw = b.cpf or ''
            cpf_limpo = re.sub(r'\D', '', cpf_raw)
            if len(cpf_limpo) == 11:
                # Se houver duplicata, preferir o ativo
                if cpf_limpo not in index or b.ativo:
                    index[cpf_limpo] = b
        logger.info(f"[SyncEngine] Índice pronto: {len(index)} CPFs únicos.")
        return index

    def execute(self, raw_data: str, contexto: str) -> Dict[str, Any]:
        """
        Executa a sincronização completa.

        Args:
            raw_data: Conteúdo bruto do arquivo (CSV como string).
            contexto: Descrição do contexto para o Memento.

        Returns:
            Dicionário com estatísticas da sincronização.
        """
        # 1. SNAPSHOT DE SEGURANÇA
        snapshot_id = self.caretaker.create_database_snapshot(
            f"[SYNC] {contexto} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        logger.info(f"[SyncEngine] Snapshot criado: ID={snapshot_id}")

        # 2. PARSE DOS DADOS
        records = self.parser.parse(raw_data)
        logger.info(f"[SyncEngine] {len(records)} registros parseados de '{self.parser.source_name}'")

        # 3. ÍNDICE IN-MEMORY (solução para CPF criptografado com Fernet)
        cpf_index = self._build_cpf_index()

        # 4. UPSERT POR CPF
        for record in records:
            try:
                self._upsert_record(record, cpf_index)
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                self._report["errors"].append(f"CPF {record.get('cpf')}: {str(e)}")
                logger.error(f"[SyncEngine] Erro no UPSERT: {e}")

        # 5. COMMIT FINAL
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.caretaker.restore_from_snapshot(snapshot_id)
            self._report["errors"].append(f"[FATAL] Commit falhou. Snapshot {snapshot_id} restaurado.")

        self._report["snapshot_id"] = snapshot_id
        return self._report

    def _upsert_record(self, record: Dict[str, Any], cpf_index: dict):
        """
        [V10.9] Enriquecimento completo por CPF (via índice in-memory):
          1. Identidade: Matrícula, Email @alunos
          2. Acadêmico: Campus, Programa, DataIngresso, PrevisaoDefesa
          3. Auditoria: DataDefesa vs DataFimBolsa → alerta antecipação
          4. Situação: status != Regular → alerta de inativação
          5. Diversidade: Sexo → DadosSociais.genero_identidade
        """
        import re
        cpf = record.get("cpf")
        bolsista = cpf_index.get(cpf)   # ← match via índice Python, não SQL

        if not bolsista:
            self._report["skipped"] += 1
            logger.info(f"[SyncEngine] CPF {cpf} não encontrado → pendente.")
            return

        # --- 1. IDENTIDADE ---
        if record.get("matricula"):
            bolsista.matricula = record["matricula"]
        email = record.get("email_academico", "")
        if email and "@alunos" in email:
            bolsista.email = email

        # --- 2. DADOS ACADÊMICOS (campos já existentes no modelo) ---
        campus_csv = record.get("campus", "")
        if campus_csv and not bolsista.campus:
            bolsista.campus = campus_csv
            bolsista.campus_sigla = campus_csv[:2].upper() if len(campus_csv) >= 2 else campus_csv

        programa_csv = record.get("programa_sigla", "")
        if programa_csv and not bolsista.programa:
            bolsista.programa = programa_csv

        ingresso_str = record.get("data_ingresso", "")
        if ingresso_str and not bolsista.data_inicio_curso:
            try:
                bolsista.data_inicio_curso = datetime.strptime(ingresso_str, "%d/%m/%Y").date()
            except ValueError:
                pass

        # --- 3. AUDITORIA DE DATAS ---
        data_defesa_str = record.get("data_defesa_str", "")
        data_fim_csv_str = record.get("data_fim_csv", "")
        data_defesa = None
        data_fim_csv = None

        if data_defesa_str:
            try:
                data_defesa = datetime.strptime(data_defesa_str, "%d/%m/%Y").date()
                # Atualiza previsao_defesa com a data real de defesa
                bolsista.previsao_defesa = data_defesa
            except ValueError:
                pass

        if data_fim_csv_str:
            try:
                data_fim_csv = datetime.strptime(data_fim_csv_str, "%d/%m/%Y").date()
            except ValueError:
                pass

        # Alerta titulação antecipada
        if data_defesa and bolsista.data_fim_bolsa and data_defesa < bolsista.data_fim_bolsa:
            self._report.setdefault("alertas_titulacao", []).append({
                "id": bolsista.id,
                "nome": bolsista.nome,
                "cpf": cpf,
                "data_defesa": data_defesa_str,
                "data_fim_bolsa": bolsista.data_fim_bolsa.strftime("%d/%m/%Y"),
                "mensagem": f"⚠️ Titulação antecipada: defendeu {data_defesa_str}, bolsa vai até {bolsista.data_fim_bolsa.strftime('%d/%m/%Y')}"
            })

        # --- 4. AUDITORIA DE SITUAÇÃO ---
        situacao = record.get("situacao", "").upper().strip()
        SITUACOES_CRITICAS = {'TITULADO', 'CANCELADO', 'DESLIGADO', 'ABANDONO', 'TRANCADO'}
        if situacao in SITUACOES_CRITICAS and bolsista.ativo:
            self._report.setdefault("alertas_situacao", []).append({
                "id": bolsista.id,
                "nome": bolsista.nome,
                "cpf": cpf,
                "situacao_acad": situacao,
                "mensagem": f"🔴 Bolsista ATIVO com situação '{situacao}' no sistema acadêmico. Verificar cancelamento."
            })

        # --- 5. DADOS SOCIAIS (tabela DadosSociais — relação 1:1) ---
        sexo = record.get("sexo", "").strip().upper()
        if sexo in ('M', 'F', 'X'):
            from models import DadosSociais
            genero_map = {'M': 'Homem Cis', 'F': 'Mulher Cis', 'X': 'Não-binário'}
            dados = bolsista.dados_sociais
            if not dados:
                dados = DadosSociais(bolsista_id=bolsista.id)
                db.session.add(dados)
            # Atualizar somente se ainda não autodeclarado manualmente
            if not dados.genero_identidade:
                dados.genero_identidade = genero_map[sexo]

        self._report["matched"] += 1

    def get_report(self) -> Dict[str, Any]:
        return self._report
