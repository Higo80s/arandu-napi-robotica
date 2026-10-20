
from models import Bolsista, Residente, db
from utils.formatters import sanitizar_cpf


def get_cpfs_efetivados_set():
    """
    Retorna um conjunto de CPFs (apenas dígitos) de bolsistas e residentes
    cadastrados (ativos e inativos). Usado no painel de seleção.
    """
    cpfs = set()

    # Query apenas a coluna CPF para performance
    # O TypeDecorator EncryptedString no SQLAlchemy descriptografa automaticamente
    try:
        results_bolsistas = db.session.query(Bolsista.cpf).all()
        for (cpf,) in results_bolsistas:
            key = sanitizar_cpf(cpf)
            if key:
                cpfs.add(key)

        results_residentes = db.session.query(Residente.cpf).all()
        for (cpf,) in results_residentes:
            key = sanitizar_cpf(cpf)
            if key:
                cpfs.add(key)
    except Exception as e:
        # Em caso de erro (ex: falha na chave de criptografia), retorna set vazio
        # para não quebrar a renderização, apenas desabilitando a trava visual.
        print(f"Erro ao carregar índice de CPFs para idempotência: {e}")

    return cpfs


def get_bolsistas_por_cpf_edital(edital_id):
    """
    Mapa CPF (só dígitos) -> {id, nome} dos bolsistas deste edital.
    Permite o painel oferecer 'Vincular' em vez de criar cadastro duplicado.
    """
    mapa = {}
    if not edital_id:
        return mapa
    try:
        rows = (
            db.session.query(Bolsista.id, Bolsista.cpf, Bolsista.nome)
            .filter(Bolsista.edital_id == edital_id)
            .all()
        )
        for bid, cpf, nome in rows:
            key = sanitizar_cpf(cpf)
            if key and key not in mapa:
                mapa[key] = {'id': bid, 'nome': (nome or '').strip()}
    except Exception as e:
        print(f"Erro ao mapear bolsistas por CPF do edital {edital_id}: {e}")
    return mapa
