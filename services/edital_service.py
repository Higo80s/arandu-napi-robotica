
from models import db, Edital
from audit import log_action
from datetime import datetime

class EditalService:
    @staticmethod
    def create_edital(data):
        """
        Cria um novo edital com validação e log de auditoria.
        """
        try:
            # Filtra dados para o modelo (evita passar csrf_token etc)
            allowed_fields = [
                'numero', 'numero_edital', 'ano_edital', 'empresa', 'descricao',
                'agencia', 'codigo_projeto', 'descricao_projeto', 'processo_sei',
                'data_inicio', 'data_fim', 'orcamento_total', 'prestacao_contas',
                'comentarios', 'proap_distribuicao_id'
            ]
            
            # Garante que proap_distribuicao_id seja None se for 0 ou inválido
            proap_id = data.get('proap_distribuicao_id')
            if proap_id is not None and (int(proap_id) <= 0):
                data['proap_distribuicao_id'] = None

            edital_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            novo_edital = Edital(**edital_data)
            db.session.add(novo_edital)
            db.session.commit()
            
            log_action('CREATE_EDITAL', tabela='editais', registro_id=novo_edital.id, 
                       detalhes=f"Numero: {novo_edital.numero} | Agencia: {novo_edital.agencia}")
            
            return True, novo_edital
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_edital(edital_id, data):
        """
        Atualiza um edital existente.
        """
        try:
            edital = Edital.query.get(edital_id)
            if not edital:
                return False, "Edital não encontrado."

            allowed_fields = [
                'numero', 'numero_edital', 'ano_edital', 'empresa', 'descricao',
                'agencia', 'codigo_projeto', 'descricao_projeto', 'processo_sei',
                'data_inicio', 'data_fim', 'orcamento_total', 'prestacao_contas',
                'comentarios', 'proap_distribuicao_id'
            ]

            # Atualiza apenas os campos permitidos
            for field in allowed_fields:
                if field in data:
                    val = data[field]
                    # Caso especial para select vazio
                    if field == 'proap_distribuicao_id' and (val is None or val == 0 or val == ''):
                        val = None
                    setattr(edital, field, val)

            db.session.commit()
            log_action('UPDATE_EDITAL', tabela='editais', registro_id=edital.id, 
                       detalhes=f"Numero: {edital.numero} atualizado")
            
            return True, edital
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_vacancy_stats(edital_id):
        """
        [NEW V10.8] Retorna estatísticas de ocupação global do edital.
        Regra: Vagas Ocupadas = Bolsistas Ativos + Candidatos SELECIONADOS (em qualquer rodada).
        """
        from models import Edital, Bolsista, Candidatura, RodadaSelecao
        
        edital = Edital.query.get(edital_id)
        if not edital:
            return {'total_vagas': 0, 'bolsistas_ativos': 0, 'selecionados': 0, 'total_ocupado': 0, 'saldo': 0}
            
        total_vagas = sum(m.vagas for m in edital.modalidades)
        
        # Bolsistas implementados e ativos
        bolsistas_ativos = Bolsista.query.filter_by(edital_id=edital_id, ativo=True).count()
        
        # Candidatos selecionados em qualquer rodada deste edital
        selecionados = db.session.query(Candidatura).join(RodadaSelecao).filter(
            RodadaSelecao.edital_id == edital_id,
            Candidatura.status == 'SELECIONADO'
        ).count()
        
        total_ocupado = bolsistas_ativos + selecionados
        saldo = total_vagas - total_ocupado
        
        return {
            'total_vagas': total_vagas,
            'bolsistas_ativos': bolsistas_ativos,
            'selecionados': selecionados,
            'total_ocupado': total_ocupado,
            'saldo': saldo
        }
