from datetime import date
from dateutil.relativedelta import relativedelta

class BolsistaStatus:
    """Constantes de Status para evitar erros de digitação e centralizar lógica"""
    ATIVO = 'ATIVO'
    SUSPENSO = 'SUSPENSO'
    FINALIZANDO = 'FINALIZANDO'
    ULTIMA_PARCELA = 'ULTIMA_PARCELA'
    CANCELAMENTO_REQUERIDO = 'CANCELAMENTO_REQUERIDO'
    VENCIDO_CRITICO = 'VENCIDO_CRITICO'
    INATIVO = 'INATIVO'
    PENDENTE_GOVERNANCA = 'PENDENTE_GOVERNANCA'
    AGUARDANDO_IMPLANTACAO = 'AGUARDANDO_IMPLANTACAO'

class StatusEngine:
    """
    [V13.1] MOTOR DE ESTADOS (Status Engineering)
    ============================================
    Calcula o status dinâmico do bolsista considerando vigência, afastamentos
    e conformidade com a Governança NAPI / implantação FA.
    """
    
    @staticmethod
    def get_status(bolsista):
        hoje = date.today()
        primeiro_dia_mes_atual = hoje.replace(day=1)

        # 0. Aguardando implantação / governança FA (antes de INATIVO)
        if getattr(bolsista, 'implantacao_pendente', False) or getattr(bolsista, 'status_governanca', None) == 'PENDENTE':
            return BolsistaStatus.AGUARDANDO_IMPLANTACAO
        
        # 1. ESTADO: INATIVO (Boolean explícito)
        if hasattr(bolsista, 'ativo') and not bolsista.ativo:
            return BolsistaStatus.INATIVO

        # 2. REGRA SOBERANA: SUSPENSO (Ex-Em Licença)
        has_active_suspension = False
        if hasattr(bolsista, 'afastamentos') and bolsista.afastamentos:
            for afasta in bolsista.afastamentos:
                data_fim_afasta = afasta.data_inicio + relativedelta(months=afasta.duracao_meses)
                if afasta.data_inicio <= hoje <= data_fim_afasta:
                    has_active_suspension = True
                    break
        
        if has_active_suspension:
            return BolsistaStatus.SUSPENSO

        # Sem vigência definida
        if not bolsista.data_fim_bolsa:
            return BolsistaStatus.AGUARDANDO_IMPLANTACAO

        # 4. ESTADO: VENCIDO CRÍTICO (> 3 meses de atraso sem desligamento)
        if bolsista.data_fim_bolsa < (primeiro_dia_mes_atual - relativedelta(months=3)):
            return BolsistaStatus.VENCIDO_CRITICO

        # 5. ESTADO: CANCELAMENTO REQUERIDO (Vencido no passado)
        if bolsista.data_fim_bolsa < primeiro_dia_mes_atual:
            return BolsistaStatus.CANCELAMENTO_REQUERIDO
            
        # 6. ESTADO: ÚLTIMA PARCELA (Vence este mês)
        if bolsista.data_fim_bolsa.month == hoje.month and bolsista.data_fim_bolsa.year == hoje.year:
             return BolsistaStatus.ULTIMA_PARCELA
            
        # 7. ESTADO: FINALIZANDO (Vence nos próximos 30 dias)
        if bolsista.data_fim_bolsa <= (hoje + relativedelta(days=30)):
            return BolsistaStatus.FINALIZANDO
            
        # 8. ESTADO: ATIVO (Vigência regular)
        return BolsistaStatus.ATIVO

    @staticmethod
    def get_display_data(status):
        """Traduz status técnico para display UI com estética Premium"""
        mapping = {
            BolsistaStatus.ATIVO: {
                'label': 'Ativo', 
                'class': 'badge-success', 
                'bg': '#d1fae5', 'color': '#065f46', 'icon': 'check-circle'
            },
            BolsistaStatus.SUSPENSO: {
                'label': 'Suspenso', 
                'class': 'badge-info', 
                'bg': '#e0f2fe', 'color': '#0369a1', 'icon': 'pause-circle'
            },
            BolsistaStatus.PENDENTE_GOVERNANCA: {
                'label': 'Aguardando implantação', 
                'class': 'badge-warning', 
                'bg': '#fef9c3', 'color': '#854d0e', 'icon': 'clock'
            },
            BolsistaStatus.AGUARDANDO_IMPLANTACAO: {
                'label': 'Aguardando implantação', 
                'class': 'badge-warning', 
                'bg': '#fef9c3', 'color': '#854d0e', 'icon': 'clock'
            },
            BolsistaStatus.CANCELAMENTO_REQUERIDO: {
                'label': 'Inativo (Vencido)', 
                'class': 'badge-danger', 
                'bg': '#fee2e2', 'color': '#991b1b', 'icon': 'alert-triangle'
            },
            BolsistaStatus.VENCIDO_CRITICO: {
                'label': 'Vencido (Crítico)', 
                'class': 'badge-danger', 
                'bg': '#7f1d1d', 'color': '#ffffff', 'icon': 'x-circle'
            },
            BolsistaStatus.ULTIMA_PARCELA: {
                'label': 'Última Parcela', 
                'class': 'badge-warning', 
                'bg': '#ffedd5', 'color': '#9a3412', 'icon': 'calendar'
            },
            BolsistaStatus.FINALIZANDO: {
                'label': 'Finalizando', 
                'class': 'badge-warning', 
                'bg': '#fff7ed', 'color': '#c2410c', 'icon': 'hourglass'
            },
            BolsistaStatus.INATIVO: {
                'label': 'Inativo', 
                'class': 'badge-secondary', 
                'bg': '#f3f4f6', 'color': '#4b5563', 'icon': 'user-x'
            }
        }
        return mapping.get(status, {'label': status, 'class': 'badge-secondary', 'bg': '#f3f4f6', 'color': '#4b5563', 'icon': 'help-circle'})
