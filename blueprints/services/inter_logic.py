from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AcordoState:
    """Snapshot para o Memento Pattern"""
    data_vencimento: any
    ativo: bool

class AcordoMemento:
    def __init__(self, state: AcordoState):
        self._state = state
    def get_state(self) -> AcordoState:
        return self._state

class MapVisualizationStrategy:
    """
    Strategy Pattern: Define como um país deve ser pintado no GeoChart.
    Valor > 1000 indica um Acordo Institucional (Cor Dourada).
    Valor < 1000 indica densidade de fluxo de alunos (Escala de Azul).
    """
    def calculate_value(self, num_alunos: int, tem_acordo: bool) -> int:
        if tem_acordo:
            return 1500 # Valor sentinela para cor de destaque
        return num_alunos

