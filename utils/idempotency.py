
from models import Bolsista, Residente, db

def get_cpfs_efetivados_set():
    """
    Retorna um conjunto (set) de CPFs (strings) de todos os bolsistas e residentes 
    cadastrados no sistema (ativos e inativos).
    Utilizado para evitar duplicidade no painel de seleção.
    """
    cpfs = set()
    
    # Query apenas a coluna CPF para performance
    # O TypeDecorator EncryptedString no SQLAlchemy descriptografa automaticamente
    try:
        results_bolsistas = db.session.query(Bolsista.cpf).all()
        for (cpf,) in results_bolsistas:
            if cpf:
                cpfs.add(cpf.strip())
                
        results_residentes = db.session.query(Residente.cpf).all()
        for (cpf,) in results_residentes:
            if cpf:
                cpfs.add(cpf.strip())
    except Exception as e:
        # Em caso de erro (ex: falha na chave de criptografia), retorna set vazio
        # para não quebrar a renderização, apenas desabilitando a trava visual.
        print(f"Erro ao carregar índice de CPFs para idempotência: {e}")
        
    return cpfs
