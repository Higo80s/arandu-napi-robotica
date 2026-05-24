from datetime import date
from decimal import Decimal
from sqlalchemy import func, or_
from models import db, Bolsista, Modalidade, Edital, Acompanhamento, UIMementoHistory, UIState
import json

class LotePaymentStrategy:
    """Strategy Pattern for Payment Lots."""
    def get_categories(self):
        raise NotImplementedError

class Lote30Strategy(LotePaymentStrategy):
    """Lote 30: FUNTEF/Pesquisadores (Dia 30)."""
    def get_categories(self):
        return ['pesquisador', 'administrativo', 'apoio', 'técnico', 'tecnico', 'gestão']

class Lote5DUStrategy(LotePaymentStrategy):
    """Lote 5º DU: Araucária/Discentes (5º Dia Útil)."""
    def get_categories(self):
        return ['iniciação científica', 'iniciacao cientifica', 'ic', 'mestrado', 'doutorado']

# --- [STRATEGY PATTERN] VENCIMENTO ---
class VencimentoStrategy:
    """Strategy Pattern for Payment Due Dates."""
    def get_vencimento_label(self):
        raise NotImplementedError

class Dia30VencimentoStrategy(VencimentoStrategy):
    """Vencimento Padrão: Dia 30."""
    def get_vencimento_label(self):
        return "Dia 30"

class QuintoDUVencimentoStrategy(VencimentoStrategy):
    """Vencimento Governança: 5º Dia Útil."""
    def get_vencimento_label(self):
        return "5º Dia Útil"

class VencimentoFactory:
    @staticmethod
    def get_strategy(edital_numero):
        if edital_numero and '03/2026' in edital_numero:
            return QuintoDUVencimentoStrategy()
        return Dia30VencimentoStrategy()

class FinanceiroService:
    TETO_PI_33_2025 = Decimal('5910124.50')

    @staticmethod
    def calculate_total_spent():
        """
        Calcula o total gasto somando os acompanhamentos de pagamento.
        Cada registro em Acompanhamento representa um pagamento mensal (valor_mensal).
        """
        spent = db.session.query(func.sum(Modalidade.valor_mensal))\
            .join(Bolsista, Modalidade.id == Bolsista.modalidade_id)\
            .join(Acompanhamento, Bolsista.id == Acompanhamento.bolsista_id)\
            .scalar() or Decimal('0')
        return spent

    @staticmethod
    def get_project_metrics():
        """
        Centraliza todas as métricas para o Dashboard Cockpit (NAPI-Robótica).
        """
        spent = FinanceiroService.calculate_total_spent()
        saldo = FinanceiroService.TETO_PI_33_2025 - spent
        
        # Projeção Mensal (Lotes)
        lote30_strat = Lote30Strategy()
        lote5du_strat = Lote5DUStrategy()
        
        lote30_sum, lote30_count = FinanceiroService._sum_by_categories(lote30_strat.get_categories())
        lote5du_sum, lote5du_count = FinanceiroService._sum_by_categories(lote5du_strat.get_categories())
        
        # Scanner de Integridade
        scanner = FinanceiroService.get_scanner_report()
        
        # Detalhamento de Vagas (Níveis e Ocupação)
        vagas_data = FinanceiroService.get_vagas_breakdown()
        
        return {
            "teto": FinanceiroService.TETO_PI_33_2025,
            "spent": spent,
            "saldo_convenio": saldo,
            "total_folha": lote30_sum + lote5du_sum,
            "lote30": lote30_sum,
            "lote5du": lote5du_sum,
            "lote30_count": lote30_count,
            "lote5du_count": lote5du_count,
            "scanner": scanner,
            "vagas_ofertadas": vagas_data['total_ofertadas'],
            "vagas_ocupadas": vagas_data['total_ocupadas'],
            "niveis": vagas_data['niveis']
        }

    @staticmethod
    def _sum_by_categories(categories):
        """Helper para somar bolsas por categorias de nível."""
        filters = [Modalidade.nivel.ilike(f'%{c}%') for c in categories]
        
        # 1. Soma Financeira
        total = db.session.query(func.sum(Modalidade.valor_mensal))\
            .join(Bolsista, Modalidade.id == Bolsista.modalidade_id)\
            .filter(Bolsista.ativo == True)\
            .filter(or_(*filters))\
            .scalar() or Decimal('0')
            
        # 2. Contagem de Bolsistas
        count = db.session.query(func.count(Bolsista.id))\
            .join(Modalidade, Modalidade.id == Bolsista.modalidade_id)\
            .filter(Bolsista.ativo == True)\
            .filter(or_(*filters))\
            .scalar() or 0
            
        return total, int(count)

    @staticmethod
    def get_scanner_report():
        """
        Detecta inconsistências críticas nos dados.
        """
        # 1. Email Orientador
        sem_email_orientador = Bolsista.query.filter(
            Bolsista.ativo == True,
            or_(Bolsista.email_orientador == None, Bolsista.email_orientador == '')
        ).count()
        
        # 2. CPF (Encrypted) - Verificando se campo existe/preenchido
        sem_cpf = Bolsista.query.filter(
            Bolsista.ativo == True,
            or_(Bolsista.cpf == None, Bolsista.cpf == '')
        ).count()
        
        # 3. Dados Bancários
        sem_banco = Bolsista.query.filter(
            Bolsista.ativo == True,
            or_(Bolsista.conta == None, Bolsista.conta == '', Bolsista.agencia == None)
        ).count()
        
        total_critico = sem_email_orientador + sem_cpf + sem_banco
        
        msg = "Sistema Íntegro"
        if total_critico > 0:
            if sem_email_orientador > 0: msg = "Bloqueio SPARKx (E-mail)"
            elif sem_cpf > 0: msg = "Pendência CPF"
            elif sem_banco > 0: msg = "Pendência Bancária"

        return {
            "total_critico": total_critico,
            "msg": msg,
            "detalhes": {
                "sem_email_orientador": sem_email_orientador,
                "sem_cpf": sem_cpf,
                "sem_banco": sem_banco
            }
        }

    @staticmethod
    def get_vagas_breakdown():
        """
        Calcula o quantitativo de vagas ocupadas vs ofertadas agrupado por nível.
        """
        # Busca todas as modalidades (Vagas Ofertadas)
        modalidades = Modalidade.query.all()
        niveis_dict = {}
        
        for m in modalidades:
            if m.nivel not in niveis_dict:
                niveis_dict[m.nivel] = {"ofertadas": 0, "ocupadas": 0}
            niveis_dict[m.nivel]["ofertadas"] += m.vagas
            
        # Conta Bolsistas Ativos (Vagas Ocupadas)
        bolsistas_ativos = Bolsista.query.filter_by(ativo=True).all()
        for b in bolsistas_ativos:
            if b.modalidade and b.modalidade.nivel:
                nivel = b.modalidade.nivel
                if nivel in niveis_dict:
                    niveis_dict[nivel]["ocupadas"] += 1
                else:
                    # Fallback para níveis não mapeados em modalidades (segurança)
                    niveis_dict[nivel] = {"ofertadas": 0, "ocupadas": 1}
        
        # Formata para lista amigável ao template
        list_niveis = []
        total_ofertadas = 0
        total_ocupadas = 0
        
        for nivel, counts in niveis_dict.items():
            list_niveis.append({
                "nome": nivel,
                "ofertadas": counts["ofertadas"],
                "ocupadas": counts["ocupadas"]
            })
            total_ofertadas += counts["ofertadas"]
            total_ocupadas += counts["ocupadas"]
            
        return {
            "total_ofertadas": total_ofertadas,
            "total_ocupadas": total_ocupadas,
            "niveis": sorted(list_niveis, key=lambda x: x['nome'])
        }

    @staticmethod
    def take_metrics_snapshot(user_id=None):
        """
        Memento Pattern: Salva o estado atual da UI/Métricas antes de um recálculo.
        """
        metrics = FinanceiroService.get_project_metrics()
        
        # Também pegamos o estado atual da tabela ui_state para o snapshot completo
        ui_records = UIState.query.all()
        ui_snapshot = {rec.element_key: rec.current_text for rec in ui_records}
        
        # Adicionamos as métricas ao snapshot para recuperação se necessário
        ui_snapshot['__metrics_snapshot__'] = metrics
        
        memento = UIMementoHistory(
            user_id=user_id,
            description=f"Snapshot automático antes de recálculo manual em {date.today()}",
            ui_snapshot=ui_snapshot
        )
        db.session.add(memento)
        db.session.commit()
        return memento.id
