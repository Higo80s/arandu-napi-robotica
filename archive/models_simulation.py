"""
MODELOS DE BANCO DE DADOS (SQLALCHEMY)
======================================

Este arquivo define a estrutura do banco de dados (Schema) da aplicação,
utilizando a biblioteca SQLAlchemy (ORM). Cada classe abaixo representa uma tabela
no arquivo SQLite (gestao_editais_new.db).

Principais Entidades:
1. Edital: O documento regulador (ex: Edital 01/2024 - PROPPG).
2. Modalidade: Categorias dentro do edital (ex: Mestrado, Doutorado) com valores e vagas.
3. Bolsista: O beneficiário final. É a tabela central que conecta Aluno -> Edital -> Programa.
4. Campus & ProgramaAcademico: Tabelas auxiliares para normalização de dados (Evita erros de digitação).

Alterações Recentes (V5/V6):
- Normalização Campus/Programa: Substituição de textos livres por chaves estrangeiras.
- Novos Campos: Processo SEI, Número do Formulário, Comentários.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inicialização do objeto DB vinculada ao Flask posteriormente
db = SQLAlchemy()

class Edital(db.Model):
    """
    Tabela: editais
    Descrição: Armazena os editais de fomento.
    """
    __tablename__ = 'editais'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False) # Ex: "01/2024"
    descricao = db.Column(db.String(200))             # Título ou resumo
    agencia = db.Column(db.String(50), nullable=False)# Ex: "CNPq", "Fundação Araucária"
    
    # Detalhes do Projeto Institucional
    codigo_projeto = db.Column(db.String(50))
    descricao_projeto = db.Column(db.Text)
    
    # Controle Administrativo (V2)
    processo_sei = db.Column(db.String(50))           # Link/Número do processo no SEI
    comentarios = db.Column(db.Text)                  # Anotações internas
    
    # [NEW V11.2 - Prod] Vigência do Edital
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    
    # [NEW V11.3 - Prod] Prestação de Contas
    prestacao_contas = db.Column(db.Boolean, default=False)

    # Relacionamentos (Cascade: Deletar Edital remove modalidades e bolsistas)
    bolsistas = db.relationship('Bolsista', backref='edital', cascade='all, delete-orphan', lazy=True)
    modalidades = db.relationship('Modalidade', backref='edital', cascade='all, delete-orphan', lazy=True)
    rodadas = db.relationship('RodadaSelecao', backref='edital', cascade='all, delete-orphan', lazy=True)
    
    @property
    def status_prestacao(self):
        """
        Retorna o status da prestação de contas:
        - 'OK': Marcado como realizada.
        - 'PENDENTE': Não marcada e data_fim vencida.
        - 'EM_ANDAMENTO': Não marcada e data_fim futura ou não definida.
        """
        from datetime import date
        if self.prestacao_contas:
            return 'OK'
        
        hoje = date.today()
        if self.data_fim and self.data_fim < hoje:
             return 'PENDENTE'
        
        return 'NORMAL'

class Modalidade(db.Model):
    """
    Tabela: modalidades
    Descrição: Define os tipos de bolsa disponíveis em um edital,
    incluindo valores financeiros e limites de tempo.
    """
    __tablename__ = 'modalidades'
    
    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id'), nullable=False)
    
    nivel = db.Column(db.String(50), nullable=False)  # Ex: "Mestrado", "Doutorado", "Iniciação Científica"
    vagas = db.Column(db.Integer, nullable=False)     # Quantidade total aprovada
    valor_mensal = db.Column(db.Float, nullable=False)# Valor da bolsa (R$)
    max_meses = db.Column(db.Integer)                 # Duração máxima permitida pelo edital (ex: 24 meses)
    
    bolsistas = db.relationship('Bolsista', backref='modalidade', lazy=True)

# [NORMALIZAÇÃO V5]
# As tabelas Campus e ProgramaAcademico evitam inconsistências de digitação.

class Campus(db.Model):
    """
    Tabela: campus
    Descrição: Lista dos 13 campi da UTFPR.
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)        # Ex: "Ponta Grossa"
    sigla_campus = db.Column(db.String(10), nullable=False) # Ex: "PG"
    
    # Relacionamento: Um Campus possui vários Programas
    programas = db.relationship('ProgramaAcademico', backref='campus', lazy=True)

class ProgramaAcademico(db.Model):
    """
    Tabela: programa_academico
    Descrição: Programas de Pós-Graduação vinculados a um Campus.
    """
    id = db.Column(db.Integer, primary_key=True)
    codigo_programa = db.Column(db.String(50)) # [UPDATED] V9: Unique constraint removed for Multicampi
    nome_programa = db.Column(db.String(200), nullable=False) # Ex: "Engenharia Mecânica"
    sigla_programa = db.Column(db.String(20), nullable=False) # Ex: "PPGEM"
    
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)

    # [NEW] V9 Fields (Dados 2025)
    nota_capes = db.Column(db.String(5))
    area_avaliacao = db.Column(db.String(100))
    area_basica = db.Column(db.String(100))
    ano_inicio = db.Column(db.Integer)

    # [NEW] V10 Field (Níveis Ofertados)
    niveis = db.Column(db.String(50)) # Ex: "M, D", "MP"

# IMPORTANT: Classes filhas (Afastamento, Acompanhamento) definidas antes de Bolsista
# para permitir configuração explícita de chaves estrangeiras.

class Afastamento(db.Model):
    """
    Tabela: afastamentos
    Descrição: Registra períodos de licença (Maternidade, Saúde) ou trancamentos.
    Impacta o cálculo da data final da bolsa.
    """
    __tablename__ = 'afastamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id'), nullable=False)
    
    tipo = db.Column(db.String(20), nullable=False)  # Opções: 'saude', 'maternidade', 'trancamento', 'pdse'
    data_inicio = db.Column(db.Date, nullable=False)
    duracao_meses = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento de volta para Bolsista
    bolsista = db.relationship('Bolsista', back_populates='afastamentos')

class Acompanhamento(db.Model):
    """
    Tabela: acompanhamentos
    Descrição: Histórico mensal de pagamentos ou status. (Futuro: Integração financeira completa)
    """
    __tablename__ = 'acompanhamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id'), nullable=False)
    
    referencia_mes = db.Column(db.String(7), nullable=False) # Formato YYYY-MM
    parcela = db.Column(db.Integer)                          # Número da parcela paga
    requisicao_pagamento = db.Column(db.String(100))         # Número do protocolo de pagamento
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Garante que só exista um registro por mês para cada bolsista
    __table_args__ = (db.UniqueConstraint('bolsista_id', 'referencia_mes', name='_bolsista_ref_uc'),)
    
    bolsista = db.relationship('Bolsista', back_populates='acompanhamentos')

class Bolsista(db.Model):
    """
    Tabela: bolsistas
    Descrição: Entidade Central do Sistema.
    Contém todos os dados pessoais, acadêmicos, bancários e de vigência da bolsa do aluno.
    """
    __tablename__ = 'bolsistas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vínculo Institucional
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id'), nullable=False)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    
    # [NEW] V5 Link: Vínculo com Programa Normalizado (Substitui campos texto legados)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True) 
    programa_link = db.relationship('ProgramaAcademico', backref=db.backref('bolsistas', lazy=True))

    # Dados Pessoais
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(100))
    
    # Dados Acadêmicos
    orientador = db.Column(db.String(100))
    email_orientador = db.Column(db.String(100)) # [NEW] V2
    
    # Campos Legados (Mantidos para compatibilidade com registros antigos pré-V5)
    campus = db.Column(db.String(50)) 
    campus_sigla = db.Column(db.String(2)) 
    programa = db.Column(db.String(100)) 
    
    data_inicio_curso = db.Column(db.Date)
    previsao_defesa = db.Column(db.Date)
    
    # Dados Bancários
    banco = db.Column(db.String(50))
    agencia = db.Column(db.String(20))
    conta = db.Column(db.String(20))
    tipo_conta = db.Column(db.String(20)) # corrente/poupanca

    # Dados da Bolsa (Vigência e Controle)
    processo_sei = db.Column(db.String(50))        # [NEW] V2: Número SEI
    numero_formulario = db.Column(db.String(50))   # [NEW] V6: Controle interno (Opcional)
    comentarios = db.Column(db.Text)               # [NEW] V2: Obs gerais
    
    is_pdse = db.Column(db.Boolean, default=False) # [NEW] V3: Flag para Sanduíche
    pais_destino = db.Column(db.String(100))       # [NEW] V3: País do Sanduíche
    
    data_inicio_bolsa = db.Column(db.Date, nullable=False)
    meses_duracao = db.Column(db.Integer, nullable=False)
    data_fim_bolsa = db.Column(db.Date, nullable=False) # Calculada automaticamente
    
    # Status e Desligamento
    ativo = db.Column(db.Boolean, default=True)
    motivo_desligamento = db.Column(db.Text)
    data_desligamento = db.Column(db.Date)
    
    # [NEW] Backup da data de fim para toggle ativo/inativo
    data_fim_bolsa_backup = db.Column(db.Date)  # Armazena data_fim_bolsa original ao desativar
    
    # [NEW] PosDoc Fields (V6.1)
    # projeto_pesquisa: Armazena o título do projeto (para bolsistas Pós-Doc)
    projeto_pesquisa = db.Column(db.String(255)) 
    # recebe_bolsa: Flag para identificar se o residente recebe bolsa ou é voluntário
    recebe_bolsa = db.Column(db.Boolean)
    # agencia_fomento: Especifica a agência (ex: "Fundação Araucária") caso difira do Edital
    agencia_fomento = db.Column(db.String(100))         
    
    def check_status_validity(self):
        """
        Calcula o status atual do bolsista baseado na data de hoje e na validade da bolsa.
        Retornos: 'INATIVO', 'FINALIZANDO' (próximo de vencer), 'ATIVO'.
        """
        from datetime import date
        hoje = date.today()
        
        # 0. Checagem Manual (Checkbox "Ativo")
        if not self.ativo:
            return 'INATIVO'
        
        # 1. Checagem de Expiração (Data já passou)
        if self.data_fim_bolsa < hoje:
            return 'INATIVO'
        
        # 2. Alerta de Vencimento (Mês Atual ou Próximo Mês)
        from dateutil.relativedelta import relativedelta
        
        next_month_date = hoje + relativedelta(months=1)
        
        is_current_month = (self.data_fim_bolsa.year == hoje.year and self.data_fim_bolsa.month == hoje.month)
        is_next_month = (self.data_fim_bolsa.year == next_month_date.year and self.data_fim_bolsa.month == next_month_date.month)
        
        if is_current_month or is_next_month:
            return 'FINALIZANDO'
        
        return 'ATIVO'
    
    # Relacionamentos Inversos (back_populates)
    # foreign_keys explícitos para resolver ambiguidade caso existam múltiplos relacionamentos
    acompanhamentos = db.relationship('Acompanhamento', back_populates='bolsista', foreign_keys=[Acompanhamento.bolsista_id], cascade='all, delete-orphan', lazy=True)
    afastamentos = db.relationship('Afastamento', back_populates='bolsista', foreign_keys=[Afastamento.bolsista_id], cascade='all, delete-orphan', lazy=True)

class Residente(db.Model):
    """
    Tabela: residentes
    Descrição: Armazena dados dos residentes pós-doutorais.
    Separado de Bolsistas para permitir ciclo de vida independente. (Modelo V7.0)
    """
    __tablename__ = 'residentes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vínculo Institucional (Nullable + Updated Constraints)
    # ondelete='SET NULL' garante que se o Edital for excluído, o residente permanece (Edital vira NULL)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id', ondelete='SET NULL'), nullable=True)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id', ondelete='SET NULL'), nullable=True)
    
    # Programa Link (Normalizado)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True)
    programa_link = db.relationship('ProgramaAcademico', backref=db.backref('residentes', lazy=True))
    
    # Edital/Modalidade Relationships
    # Definir aqui para não poluir a classe Edital original com mais relacionamentos agora
    edital = db.relationship('Edital', backref=db.backref('residentes', lazy=True))
    modalidade = db.relationship('Modalidade', backref=db.backref('residentes', lazy=True))

    # Dados Pessoais
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(100))
    
    # Dados Específicos Pós-Doc
    supervisor = db.Column(db.String(100))       # Equivalente a Orientador
    projeto_pesquisa = db.Column(db.String(255)) 
    agencia_fomento = db.Column(db.String(100))  
    recebe_bolsa = db.Column(db.Boolean, default=True)

    # Dados da Bolsa/Vigência
    processo_sei = db.Column(db.String(50))
    numero_formulario = db.Column(db.String(50)) # Added in V7.1 fix
    data_inicio = db.Column(db.Date, nullable=False) # data_inicio_bolsa
    data_fim = db.Column(db.Date, nullable=False)    # data_fim_bolsa
    meses_duracao = db.Column(db.Integer)
    
    # Status
    ativo = db.Column(db.Boolean, default=True)
    
    # Métodos Auxiliares
    def check_status_validity(self):
        from datetime import date
        hoje = date.today()
        if not self.ativo: return 'INATIVO'
        if self.data_fim < hoje: return 'INATIVO'
        return 'ATIVO'

# [NEW V8] Módulo de Seleção e Cronogramas
# ========================================

class RodadaSelecao(db.Model):
    """
    Tabela: rodadas_selecao
    Descrição: Representa um ciclo de seleção dentro de um Edital.
    Ex: "Chamada Regular 2025/1", "Vagas Remanescentes", "Edital Suplementar".
    """
    __tablename__ = 'rodadas_selecao'
    
    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False) # Ex: "Chamada Regular"
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    ativa = db.Column(db.Boolean, default=True)      # Se é a chamada atual
    descricao = db.Column(db.Text)
    
    # Relações
    etapas = db.relationship('EtapaCronograma', backref='rodada', cascade='all, delete-orphan', lazy=True)
    candidaturas = db.relationship('Candidatura', backref='rodada', cascade='all, delete-orphan', lazy=True)

class EtapaCronograma(db.Model):
    """
    Tabela: etapas_cronograma
    Descrição: Etapas específicas de um cronograma (Inscrição, Resultados, etc).
    """
    __tablename__ = 'etapas_cronograma'
    
    id = db.Column(db.Integer, primary_key=True)
    rodada_id = db.Column(db.Integer, db.ForeignKey('rodadas_selecao.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False) # Ex: "Inscrições Abertas"
    data_inicio = db.Column(db.Date)                 # [NEW V10] Início do período
    data_limite = db.Column(db.Date)                 # Fim do período (Deadline)
    ordem = db.Column(db.Integer, default=0)         # Para ordenação visual
    concluida = db.Column(db.Boolean, default=False)
    link_publicacao = db.Column(db.String(255))      # Link para PDF oficial (Editais de Resultado)
    
class Candidatura(db.Model):
    """
    Tabela: candidaturas
    Descrição: Registro de interessados na bolsa. Separa "Candidato" de "Bolsista".
    Se aprovado, um registro em 'bolsistas' é criado (Promoção).
    """
    __tablename__ = 'candidaturas'
    
    id = db.Column(db.Integer, primary_key=True)
    rodada_id = db.Column(db.Integer, db.ForeignKey('rodadas_selecao.id'), nullable=False)
    
    # Dados do Candidato
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    email = db.Column(db.String(100))
    
    # [NEW V10] Dados do Projeto/Orientação
    orientador = db.Column(db.String(100))
    email_orientador = db.Column(db.String(100))
    projeto_pesquisa = db.Column(db.String(255))
    
    # Dados Acadêmicos (Alvo)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=True) # Pode ser nulo incialmente? Melhor não.
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True)
    
    # Controle
    numero_sei = db.Column(db.String(50))
    numero_formulario = db.Column(db.String(50))
    anotacoes = db.Column(db.Text)
    
    # Status do Funil
    # INSCRITO, SELECIONADO, EXCEDENTE, DESCLASSIFICADO, BOLSISTA (Promovido)
    status = db.Column(db.String(20), default='INSCRITO') 
    
    data_submissao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campus = db.relationship('Campus')
    programa = db.relationship('ProgramaAcademico')

