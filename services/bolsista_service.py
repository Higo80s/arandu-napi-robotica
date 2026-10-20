
from datetime import date
from dateutil.relativedelta import relativedelta
from models import db, Bolsista, Modalidade, ProgramaAcademico, Candidatura
from audit import log_action

class BolsistaService:
    @staticmethod
    def calculate_end_date(data_inicio_bolsa, meses_duracao, afastamentos):
        """
        Calcula a data final da bolsa considerando suspensões/afastamentos.
        Retorna None enquanto a vigência não estiver definida.
        """
        if not data_inicio_bolsa or not meses_duracao:
            return None

        ext_suspension = 0
        for afast in afastamentos:
            if afast.get('tipo') in ['trancamento', 'saude', 'pdse']:
                ext_suspension += int(afast.get('duracao_meses', 0))
        
        return data_inicio_bolsa + relativedelta(months=(meses_duracao - 1 + ext_suspension))

    @staticmethod
    def validate_vacancy(modalidade_id):
        """
        Verifica se há vagas disponíveis na modalidade.
        """
        mod = Modalidade.query.get(modalidade_id)
        if not mod:
            return False, "Modalidade não encontrada."

        # Reserva vaga também para cadastros aguardando implantação/governança
        occupied_count = Bolsista.query.filter(
            Bolsista.modalidade_id == modalidade_id,
            db.or_(
                Bolsista.ativo.is_(True),
                Bolsista.implantacao_pendente.is_(True),
                Bolsista.status_governanca == 'PENDENTE',
            ),
        ).count()
        if occupied_count >= mod.vagas:
            return False, f"Limite de Vagas Esgotado! Esta modalidade possui {mod.vagas} vagas."
            
        return True, None

    @staticmethod
    def sync_candidacy(candidatura_id, bolsista_cpf, bolsista_id=None):
        """
        Efetiva a candidatura vinculada ao bolsista.
        """
        if not candidatura_id:
            return False

        cand = Candidatura.query.get(candidatura_id)
        if not cand:
            return False
        cand.status = 'EFETIVADO'
        detalhes = f"Candidatura {candidatura_id} efetivada para o CPF {bolsista_cpf}"
        if bolsista_id:
            detalhes += f" (bolsista_id={bolsista_id})"
        log_action(
            'EFETIVAR_CANDIDATURA',
            tabela='candidaturas',
            registro_id=cand.id,
            detalhes=detalhes,
        )
        db.session.commit()
        return True

    @staticmethod
    def find_by_cpf_edital(cpf, edital_id):
        """Localiza bolsista do edital com o mesmo CPF (comparação só por dígitos)."""
        from utils.formatters import sanitizar_cpf

        key = sanitizar_cpf(cpf)
        if not key or not edital_id:
            return None
        for bol in Bolsista.query.filter_by(edital_id=edital_id).all():
            if sanitizar_cpf(bol.cpf) == key:
                return bol
        return None

    @staticmethod
    def vincular_candidatura_existente(candidatura, bolsista=None):
        """
        Marca candidatura como EFETIVADO apontando para bolsista já cadastrado
        no mesmo edital (evita criar segundo registro).
        """
        if not candidatura:
            return False, 'Candidatura não encontrada.'
        edital_id = candidatura.rodada.edital_id if candidatura.rodada else None
        bolsista = bolsista or BolsistaService.find_by_cpf_edital(candidatura.cpf, edital_id)
        if not bolsista:
            return False, 'Nenhum bolsista com este CPF neste edital.'
        ok = BolsistaService.sync_candidacy(
            candidatura.id, bolsista.cpf, bolsista_id=bolsista.id
        )
        if not ok:
            return False, 'Não foi possível efetivar a candidatura.'
        log_action(
            'VINCULAR_CANDIDATURA_BOLSISTA',
            tabela='candidaturas',
            registro_id=candidatura.id,
            detalhes=(
                f"Candidatura {candidatura.id} vinculada ao bolsista {bolsista.id} "
                f"({bolsista.nome})."
            ),
        )
        db.session.commit()
        return True, bolsista

    @staticmethod
    def calculate_current_installment(bolsista):
        """
        Calcula a parcela atual (X) baseada na Competência Trabalhada.
        X = (Ano_atual - Ano_inicio) * 12 + (Mes_atual - Mes_inicio) + 1
        """
        if not bolsista.ativo or not bolsista.data_inicio_bolsa:
            return 0
            
        hoje = date.today()
        # Se hoje for anterior à data de início, ainda é a primeira parcela (ou zero se futuro distante)
        if hoje < bolsista.data_inicio_bolsa:
            return 1
            
        diff_anos = hoje.year - bolsista.data_inicio_bolsa.year
        diff_meses = hoje.month - bolsista.data_inicio_bolsa.month
        
        X = (diff_anos * 12) + diff_meses + 1
        
        # Não pode exceder a duração total
        if X > bolsista.meses_duracao:
            return bolsista.meses_duracao
            
        return X

    @staticmethod
    def get_5th_business_day(year, month):
        """
        [GOVERNANÇA NAPI] Calcula o 5º dia útil do mês.
        Considera Sábados, Domingos e Feriados Nacionais (Brasil).
        """
        import calendar
        
        # Feriados Nacionais Fixos
        feriados_fixos = [
            (1, 1),   # Confraternização Universal
            (21, 4),  # Tiradentes
            (1, 5),   # Dia do Trabalho
            (7, 9),   # Independência
            (12, 10), # Nsa. Sra. Aparecida
            (2, 11),  # Finados
            (15, 11), # Proclamação da República
            (20, 11), # Consciência Negra
            (25, 12), # Natal
        ]
        
        # Feriados Móveis 2026 (Simplificado para o ano vigente)
        # 17/02: Carnaval, 03/04: Sexta Santa, 04/06: Corpus Christi
        feriados_moveis_2026 = [(17, 2), (3, 4), (4, 6)]
        
        def is_feriado(d, m, y):
            if (d, m) in feriados_fixos: return True
            if y == 2026 and (d, m) in feriados_moveis_2026: return True
            return False

        cnt = 0
        for day in range(1, 15):
            dt = date(year, month, day)
            weekday = dt.weekday()
            
            if weekday < 5 and not is_feriado(day, month, year):
                cnt += 1
            
            if cnt == 5:
                return dt
        return date(year, month, 7) # Fallback

    @staticmethod
    def validate_governance_dates(bolsista_data, bolsista_id=None):
        """
        [PI 33/2026] Validações estritas de datas.
        """
        data_inicio = bolsista_data.get('data_inicio_bolsa')
        data_curso = bolsista_data.get('data_inicio_curso')
        data_defesa = bolsista_data.get('previsao_defesa')
        
        if isinstance(data_inicio, str): data_inicio = date.fromisoformat(data_inicio)
        if isinstance(data_curso, str): data_curso = date.fromisoformat(data_curso)
        if isinstance(data_defesa, str): data_defesa = date.fromisoformat(data_defesa)

        # 1. Início da Bolsa não pode ser anterior ao Início do Curso
        if data_inicio and data_curso and data_inicio < data_curso:
            return False, "Regra de Governança: A data de início da bolsa não pode ser anterior ao início do curso."
            
        # 2. Início da Bolsa não pode ser posterior à Previsão de Defesa
        if data_inicio and data_defesa and data_inicio > data_defesa:
            return False, "Erro Grave: Data de início da bolsa após a previsão de defesa."
            
        return True, None

    @staticmethod
    def activate_bolsista(id, data_liberacao):
        """
        [PI 33/2026] Ativação manual de bolsistas Pendentes.
        Vigência começa na data de liberação da Fundação Araucária.
        """
        bolsista = Bolsista.query.get(id)
        if not bolsista: return False, "Bolsista não encontrado."

        from services.funtef_onboarding_service import FuntefOnboardingService
        from services.implantacao_bolsa_service import ImplantacaoBolsaService

        ok, msg = FuntefOnboardingService.can_activate(bolsista)
        if not ok:
            return False, msg

        pendencias = ImplantacaoBolsaService.pendencias(bolsista, exigir_inicio=False)
        if pendencias:
            return False, pendencias[0]
        
        if isinstance(data_liberacao, str):
            data_liberacao = date.fromisoformat(data_liberacao)
            
        # Snapshot de segurança (Memento)
        bolsista.create_snapshot(contexto=f"Ativação Governança - Liberação: {data_liberacao}")
        
        bolsista.status_governanca = 'ATIVO'
        bolsista.ativo = True
        bolsista.implantacao_pendente = False
        bolsista.data_liberacao_fundacao = data_liberacao
        
        # Ajusta data_inicio_bolsa para ser a data de liberação
        bolsista.data_inicio_bolsa = data_liberacao
        
        # [NEW] Limpa dados de desligamento residual (caso estivesse desativado anteriormente)
        bolsista.data_desligamento = None
        bolsista.motivo_desligamento = None
        bolsista.ultimo_mes_email_competencia = None
        bolsista.ultimo_mes_email_enviado_em = None
        
        # Recalcula data_fim_bolsa
        bolsista.data_fim_bolsa = BolsistaService.calculate_end_date(
            bolsista.data_inicio_bolsa, 
            bolsista.meses_duracao, 
            []
        )

        ImplantacaoBolsaService.registrar_ativacao(bolsista)
        
        db.session.commit()
        log_action('ATIVACAO_GOVERNANCA', tabela='bolsistas', registro_id=id, 
                   detalhes=f"Ativado com liberação em {data_liberacao}. Vigência recalculada.")
        
        return True, "Bolsista ativado com sucesso. Vigência sincronizada com a Fundação Araucária."

    @staticmethod
    def trigger_sparkx_onboarding(bolsista):
        """
        Trigga o e-mail de onboarding para o SPARKx.
        Verifica se há e-mail do orientador (Scanner de Integridade).
        """
        if not bolsista.email_orientador:
            log_action('SPARKX_LOG', tabela='bolsistas', registro_id=bolsista.id, 
                       detalhes=f"ONBOARDING BLOQUEADO: Orientador sem e-mail para {bolsista.nome}")
            return False, "Bloqueio de Integridade: E-mail do orientador ausente."

        # Simulação de envio de e-mail (Log de Auditoria)
        corpo = f"""
        Olá {bolsista.nome}, bem-vindo ao projeto NAPI-Robótica!
        Para iniciar suas atividades, realize seu cadastro no SPARKx.
        
        IMPORTANTE: 
        - Use seu NOME COMPLETO POR EXTENSO.
        - Respeite o seu NOME SOCIAL caso esteja cadastrado.
        
        Link: https://sparkx.napi-robotica.org.br/onboarding
        """
        
        log_action('SPARKX_EMAIL_SENT', tabela='bolsistas', registro_id=bolsista.id, 
                   detalhes=f"E-mail enviado para {bolsista.email}. Orientador: {bolsista.email_orientador}")
        
        return True, "E-mail de onboarding SPARKx disparado com sucesso."
