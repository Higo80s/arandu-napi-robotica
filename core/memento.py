from copy import deepcopy

class BolsistaMemento:
    """O 'Memento' armazena o retrato do estado do Bolsista."""
    def __init__(self, state: dict):
        self._state = deepcopy(state)
        
    def get_state(self) -> dict:
        return self._state

class BolsistaCaretaker:
    """Gerencia o Histórico (Stack) para Undo/Redo na memória."""
    def __init__(self):
        self._mementos = []
        
    def backup(self, bolsista):
        """Salva o estado atual na pilha usando to_dict()."""
        # Supondo que to_dict() não exija transação com o BD ativo e gere um JSON limpo
        state = {
            "id": bolsista.id,
            "nome": bolsista.nome,
            "cpf": bolsista.cpf,
            "registro_academico": bolsista.registro_academico,
            "ativo": bolsista.ativo,
            "edital_id": bolsista.edital_id,
            "modalidade_id": bolsista.modalidade_id
        }
        self._mementos.append(BolsistaMemento(state))
        
    def undo(self, bolsista):
        """Restaura o último estado salvo no objeto atual."""
        if not self._mementos:
            return
            
        memento = self._mementos.pop()
        state = memento.get_state()
        
        # Restauração das propriedades vitais que podem ter sido alteradas antes do erro
        bolsista.nome = state.get('nome')
        bolsista.cpf = state.get('cpf')
        bolsista.registro_academico = state.get('registro_academico')
        bolsista.ativo = state.get('ativo')
        bolsista.edital_id = state.get('edital_id')
        bolsista.modalidade_id = state.get('modalidade_id')

    def create_database_snapshot(self, contexto_msg):
        """
        [NEW V10.8] Cria um ponto de restauração persistente no banco de dados.
        """
        from models import Bolsista, DatabaseMemento, db
        import json
        
        bolsistas_atuais = Bolsista.query.all()
        data_list = []
        for b in bolsistas_atuais:
            data_list.append({
                'cpf': b.cpf,
                'matricula': b.matricula,
                'email': b.email,
                'data_fim_bolsa': b.data_fim_bolsa.isoformat() if b.data_fim_bolsa else None,
                'ativo': b.ativo,
                'programa_id': b.programa_id
            })
            
        memento = DatabaseMemento(
            contexto=contexto_msg,
            snapshot_data=data_list,
            total_registros=len(data_list)
        )
        
        db.session.add(memento)
        db.session.commit()
        return memento.id

    def restore_from_snapshot(self, memento_id):
        """
        [NEW V10.8] Restaura o estado do banco a partir de um snapshot persistente.
        """
        from models import Bolsista, DatabaseMemento, db
        
        memento = DatabaseMemento.query.get(memento_id)
        if not memento:
            return False, "Snapshot não encontrado."
            
        data_list = memento.snapshot_data
        for item in data_list:
            b = Bolsista.query.filter_by(cpf=item['cpf']).first()
            if b:
                b.matricula = item.get('matricula')
                b.email = item.get('email')
                b.ativo = item.get('ativo')
                # Restauração de datas exige parse
                from datetime import date
                dfb = item.get('data_fim_bolsa')
                b.data_fim_bolsa = date.fromisoformat(dfb) if dfb else None
                
        db.session.commit()
        return True, f"Restaurados {len(data_list)} registros com sucesso."
