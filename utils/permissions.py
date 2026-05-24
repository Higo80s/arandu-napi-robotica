"""
Módulo de Permissões e Controle de Acesso

Implementa sistema de filtros baseado em roles hierárquicos para
restringir visualização e edição de dados conforme escopo do usuário.

Roles Suportados:
- admin: Acesso total
- diretor_campus: Vê todos programas de um campus
- coordenador_programa: Vê apenas um programa específico
- gestor: Acesso total (legacy)
- visualizador: Apenas leitura

Uso:
    from utils.permissions import apply_user_scope, can_edit_model
    
    query = Bolsista.query
    query = apply_user_scope(query, current_user, Bolsista)
    bolsistas = query.all()
"""

from flask_login import current_user
from extensions import db
from models import Bolsista, Edital, ProgramaAcademico, Campus

def apply_user_scope(query, user, model):
    """
    Aplica filtro de escopo baseado no role do usuário.
    
    Args:
        query: SQLAlchemy query object
        user: User object (current_user)
        model: Model class sendo consultado (Bolsista, Edital, etc)
    
    Returns:
        Query filtrada pelo escopo do usuário
    """
    # Admin, Master e Gestor: acesso total
    if user.role in ['admin', 'master', 'gestor']:
        return query
    
    # Diretor de Campus: vê todos programas do campus
    if user.role == 'diretor_campus' and user.campus_id:
        if model == Bolsista:
            # Filtrar bolsistas por programas do campus
            query = query.join(ProgramaAcademico).filter(
                ProgramaAcademico.campus_id == user.campus_id
            )
        elif model == Edital:
            # Editais também podem ter relacionamento com campus via programa
            # (adaptar conforme modelo Edital)
            pass
        return query
    
    # Coordenador de Programa: vê apenas seu programa
    if user.role == 'coordenador_programa' and user.programa_id:
        if model == Bolsista:
            query = query.filter(Bolsista.programa_id == user.programa_id)
        elif model == Edital:
            # Filtrar editais por programa se houver relacionamento
            pass
        return query
    
    # Visualizador: acesso total mas read-only (filtrado na UI)
    if user.role == 'visualizador':
        return query
    
    # Sem permissão: retorna query vazia
    return query.filter(False)


def can_edit_model(user, model_instance=None):
    """
    Verifica se usuário pode editar um determinado modelo/instância.
    
    Args:
        user: User object
        model_instance: Instância do modelo a ser editada (opcional)
    
    Returns:
        Boolean indicando se pode editar
    """
    # Admin, Master e Gestor: sempre podem editar
    if user.role in ['admin', 'master', 'gestor']:
        return True
    
    # Visualizador: nunca pode editar
    if user.role == 'visualizador':
        return False
    
    # Se não há instância, verificar apenas role
    if not model_instance:
        return user.role in ['diretor_campus', 'coordenador_programa']
    
    # Diretor de Campus: pode editar se o modelo pertence ao seu campus
    if user.role == 'diretor_campus' and user.campus_id:
        if isinstance(model_instance, Bolsista):
            return model_instance.programa.campus_id ==user.campus_id
        return True  # Outros modelos: permitir por padrão
    
    # Coordenador de Programa: pode editar se o modelo pertence ao seu programa
    if user.role == 'coordenador_programa' and user.programa_id:
        if isinstance(model_instance, Bolsista):
            return model_instance.programa_id == user.programa_id
        return False  # Outros modelos: negar por padrão
    
    return False


def can_create_model(user, model_class):
    """
    Verifica se usuário pode criar novo registro de um modelo.
    
    Args:
        user: User object
        model_class: Classe do modelo (Bolsista, Edital, etc)
    
    Returns:
        Boolean indicando se pode criar
    """
    # Visualizador: nunca pode criar
    if user.role == 'visualizador':
        return False
    
    # Admin, Master, Gestor, Diretor, Coordenador: podem criar
    return user.role in ['admin', 'master', 'gestor', 'diretor_campus', 'coordenador_programa']


def can_delete_model(user, model_instance):
    """
    Verifica se usuário pode excluir um modelo.
    
    Args:
        user: User object
        model_instance: Instância do modelo a ser excluída
    
    Returns:
        Boolean indicando se pode excluir
    """
    # Apenas Admin, Master e Gestor podem excluir
    # (Coordenadores e Diretores NÃO podem excluir)
    return user.role in ['admin', 'master', 'gestor']


def get_scope_description(user):
    """
    Retorna descrição textual do escopo do usuário.
    
    Args:
        user: User object
    
    Returns:
        String descrevendo o escopo de acesso
    """
    if user.role == 'admin':
        return "Acesso total ao sistema (Administrador)"
    
    if user.role == 'master':
        return "Acesso total ao sistema (Master)"
    
    if user.role == 'gestor':
        return "Acesso total ao sistema (Gestor)"
    
    if user.role == 'diretor_campus' and user.campus:
        return f"Campus {user.campus.nome} ({user.campus.sigla_campus})"
    
    if user.role == 'coordenador_programa' and user.programa:
        return f"Programa {user.programa.nome_programa}"
    
    if user.role == 'visualizador':
        return "Visualização (somente leitura)"
    
    return "Sem escopo definido"


def filter_editais_by_scope(query, user):
    """
    Filtra editais baseado no escopo do usuário.
    Coordenadores veem apenas editais onde seu programa tem bolsistas.
    
    Args:
        query: SQLAlchemy query object de Edital
        user: User object
    
    Returns:
        Query filtrada
    """
    from models import Bolsista, ProgramaAcademico, Edital
    
    # Admin, Master e Gestor: acesso total
    if user.role in ['admin', 'master', 'gestor']:
        return query
    
    # Coordenador: editais onde o programa tem bolsistas
    if user.role == 'coordenador_programa' and user.programa_id:
        # Subquery para IDs de editais com bolsistas do programa
        editais_ids = db.session.query(Bolsista.edital_id).filter(
            Bolsista.programa_id == user.programa_id
        ).distinct().subquery()
        
        query = query.filter(Edital.id.in_(editais_ids))
        return query
    
    # Diretor: editais onde programas do campus têm bolsistas
    if user.role == 'diretor_campus' and user.campus_id:
        # Subquery para IDs de editais com bolsistas do campus
        editais_ids = db.session.query(Bolsista.edital_id).join(
            ProgramaAcademico
        ).filter(
            ProgramaAcademico.campus_id == user.campus_id
        ).distinct().subquery()
        
        query = query.filter(Edital.id.in_(editais_ids))
        return query
    
    # Visualizador: acesso total
    if user.role == 'visualizador':
        return query
    
    # Sem permissão
    return query.filter(False)
