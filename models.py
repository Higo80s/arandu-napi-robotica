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
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import JSONB
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db # [REFATORACAO] Instancia centralizada
from core.datetime_utils import utc_now
from sqlalchemy.orm import validates
from sqlalchemy import event, or_
from encryption import EncryptedString
# db = SQLAlchemy() -> Removido (v6.3)

class User(UserMixin, db.Model):
    """
    Tabela: usuarios
    Descrição: Usuários do sistema com controle de acesso.
    
    Roles Suportados:
    - admin: Acesso total ao sistema
    - diretor_campus: Acesso a todos programas de um campus específico
    - coordenador_programa: Acesso apenas a um programa específico
    - gestor: Acesso total (legacy, similar a admin)
    - visualizador: Apenas leitura
    """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), default='visualizador') # admin, diretor_campus, coordenador_programa, gestor, visualizador
    ativo = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False)
    ultimo_acesso = db.Column(db.DateTime)
    
    # [V22] Campos de Escopo para Roles Hierárquicos
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=True)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

# ============================================================================
# MÓDULO PROAP/PROAPINHO (FASE 8)
# ============================================================================

class ProapRepasse(db.Model):
    """
    Tabela: proap_repasses
    Descrição: Registro de repasses PROAP (CAPES) e PROAPINHO (UTFPR) anuais.
    
    PROAP: Programa de Apoio à Pós-Graduação (CAPES)
    PROAPINHO: Programa institucional UTFPR de complementação ao PROAP
    """
    __tablename__ = 'proap_repasses'
    
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False, index=True)  # Ex: 2024, 2025
    tipo = db.Column(db.String(20), nullable=False)          # 'PROAP' ou 'PROAPINHO'
    valor_total = db.Column(db.Numeric(12, 2), nullable=False)        # Valor total do repasse
    data_repasse = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    distribuicoes = db.relationship('ProapDistribuicao', backref='repasse', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ProapRepasse {self.tipo} {self.ano} - R$ {self.valor_total:,.2f}>"


class ProapDistribuicao(db.Model):
    """
    Tabela: proap_distribuicoes
    Descrição: Distribuição de recursos PROAP/PROAPINHO para programas de pós-graduação.
    
    Cada linha representa quanto de um determinado repasse foi alocado para um programa específico.
    Inclui rastreamento via número SEI para conformidade administrativa.
    """
    __tablename__ = 'proap_distribuicoes'
    
    id = db.Column(db.Integer, primary_key=True)
    repasse_id = db.Column(db.Integer, db.ForeignKey('proap_repasses.id'), nullable=False, index=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=False, index=True)
    
    # Valores financeiros
    valor_distribuido = db.Column(db.Numeric(12, 2), nullable=False)
    percentual = db.Column(db.Numeric(12, 4))  # Percentual do repasse total (calculado)
    data_distribuicao = db.Column(db.Date, nullable=False)
    
    # Rastreamento administrativo (Adicionado com base no feedback do usuário)
    numero_sei = db.Column(db.String(50))  # Processo SEI da distribuição
    anotacoes = db.Column(db.Text)         # Observações administrativas
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    programa = db.relationship('ProgramaAcademico', backref='proap_distribuicoes', lazy=True)
    aplicacoes = db.relationship('ProapAplicacao', backref='distribuicao', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ProapDistribuicao Programa={self.programa_id} - R$ {self.valor_distribuido:,.2f}>"


class ProapAplicacao(db.Model):
    """
    Tabela: proap_aplicacoes
    Descrição: Registro de aplicação/despesa dos recursos PROAP/PROAPINHO.
    
    Categorias permitidas (Portaria CAPES nº 156/2014):
    - Manutenção de equipamentos e laboratórios
    - Participação em eventos, cursos, treinamentos, intercâmbios
    - Produção e divulgação científica (revisão, tradução, publicação)
    - Apoio a convidados externos e pesquisadores
    - Tecnologias de informação e acervos especializados
    """
    __tablename__ = 'proap_aplicacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    distribuicao_id = db.Column(db.Integer, db.ForeignKey('proap_distribuicoes.id'), nullable=False, index=True)
    
    # Classificação da despesa
    categoria = db.Column(db.String(100), nullable=False, index=True)  # Ver lista acima
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Numeric(12, 2), nullable=False)
    data_aplicacao = db.Column(db.Date, nullable=False, index=True)
    
    # Documentação fiscal
    numero_documento = db.Column(db.String(50))  # Nota fiscal, recibo, etc.
    arquivo_comprovante = db.Column(db.String(255))  # Path do arquivo PDF/imagem
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProapAplicacao {self.categoria} - R$ {self.valor:,.2f}>"


# Constantes para validação de categorias
CATEGORIAS_PROAP = [
    'Manutenção de Equipamentos',
    'Manutenção de Laboratórios',
    'Participação em Eventos',
    'Cursos e Treinamentos',
    'Intercâmbios Acadêmicos',
    'Produção Científica',
    'Tradução e Revisão',
    'Publicações',
    'Convidados Externos',
    'Pesquisadores Visitantes',
    'Tecnologia da Informação',
    'Acervos Especializados',
    'Outros'
]

class Edital(db.Model):
    """
    Tabela: editais
    Descrição: Armazena os editais de fomento.
    """
    __tablename__ = 'editais'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False) # Ex: "01/2024"
    descricao = db.Column(db.Text)                    # Título ou resumo [UPDATED V20: Text p/ Postgres]
    agencia = db.Column(db.String(50), nullable=False)# Ex: "CNPq", "Fundação Araucária"
    
    # Detalhes do Projeto Institucional
    codigo_projeto = db.Column(db.String(150))        # [UPDATED V20] Aumentado para 150
    descricao_projeto = db.Column(db.Text)
    
    # Controle Administrativo (V2)
    processo_sei = db.Column(db.String(100))          # Link/Número do processo no SEI [UPDATED V20]
    comentarios = db.Column(db.Text)                  # Anotações internas
    regras_anotacoes = db.Column(db.Text)             # [NEW] Observações sobre normas de acúmulo e afins
    
    # [NEW V11.8] Design Patterns: Atomic Fields
    numero_edital = db.Column(db.String(150))          # Ex: "01", "002"
    ano_edital = db.Column(db.Integer)                 # Ex: 2024, 2025
    empresa = db.Column(db.String(150))                # [NEW] Empresa/Parceiro vinculado ao fomento
    numero_convenio = db.Column(db.String(100))        # Ex: "CONV 110/2025"
    coordenador_geral_proppg = db.Column(db.String(200))  # Coordenador Geral do Projeto / PROPPG

    # [NEW V11.2 - Prod] Vigência do Edital
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    
    # [NEW V11.3 - Prod] Prestação de Contas
    prestacao_contas = db.Column(db.Boolean, default=False)
    
    # [NEW Phase 2.1] Eixo Estratégico NAPI (Difusão, Educação, Inovação)
    eixo = db.Column(db.String(100), default='Geral/Pendentes')

    # [NEW Phase 3] Controle Orçamentário Global
    orcamento_total = db.Column(db.Numeric(12, 2), default=0.0)

    # Relacionamentos (Cascade: Deletar Edital remove modalidades e bolsistas)
    bolsistas = db.relationship('Bolsista', backref='edital', cascade='all, delete-orphan', lazy=True)
    modalidades = db.relationship('Modalidade', backref='edital', cascade='all, delete-orphan', lazy=True)
    # [NEW V10] Módulo Seleção
    rodadas = db.relationship('RodadaSelecao', backref='edital', cascade='all, delete-orphan', lazy=True, order_by='RodadaSelecao.ordem')
    # [NEW FASE E] Regras Dinâmicas (Módulo Seleção)
    regras = db.relationship('EditalRegra', backref='edital', cascade='all, delete-orphan', lazy=True, order_by='EditalRegra.ordem')
    comentarios_historico = db.relationship('ComentarioEdital', back_populates='edital', cascade='all, delete-orphan', lazy=True, order_by='ComentarioEdital.criado_em.asc()')
    
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

    # [NEW FASE 9] Integração PROAP - Fonte de Recurso
    proap_distribuicao_id = db.Column(db.Integer, db.ForeignKey('proap_distribuicoes.id'), nullable=True)
    proap_distribuicao = db.relationship('ProapDistribuicao', backref='editais_vinculados', lazy=True)

class EditalRegra(db.Model):
    """
    Tabela: edital_regras
    Descrição: Regras dinâmicas do edital para consulta rápida no Painel de Seleção.
    """
    __tablename__ = 'edital_regras'
    
    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id', ondelete='CASCADE'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    ordem = db.Column(db.Integer, default=0)


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
    valor_mensal = db.Column(db.Numeric(12, 2), nullable=False)# Valor da bolsa (R$)
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
    instituicao = db.Column(db.String(255))                 # Ex: "UTFPR", "UEM", "USP"
    nome = db.Column(db.String(100), nullable=False)        # Ex: "Curitiba", "Ponta Grossa"
    cidade = db.Column(db.String(100))                      # Ex: "São Paulo", "Maringá"
    sigla_campus = db.Column(db.String(20), nullable=False) # Ex: "PG", "USP-SP"
    
    # Relacionamento: Um Campus possui vários Programas
    programas = db.relationship('ProgramaAcademico', backref='campus', lazy=True)

class ProgramaAcademico(db.Model):
    """
    Tabela: programa_academico
    Descrição: Programas de Pós-Graduação vinculados a um Campus.
    """
    id = db.Column(db.Integer, primary_key=True)
    codigo_programa = db.Column(db.String(50)) # [UPDATED] V9: Unique constraint removed for Multicampi
    nome_programa = db.Column(db.String(500), nullable=False) # Ex: "Engenharia Mecânica" [UPDATED V20]
    sigla_programa = db.Column(db.String(20), nullable=False) # Ex: "PPGEM"
    
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)

    # Níveis Ofertados
    niveis = db.Column(db.String(50)) # Ex: "M, D", "MP"

    def get_niveis_list(self):
        if not self.niveis:
            return []
        return [n.strip() for n in self.niveis.split(',')]

    @property
    def is_multicampi(self):
        if not self.codigo_programa:
            return False
        return ProgramaAcademico.query.filter_by(codigo_programa=self.codigo_programa).count() > 1

    def get_related_campus_ids(self):
        if not self.codigo_programa:
            return [self.campus_id]
        return [p.campus_id for p in ProgramaAcademico.query.filter_by(codigo_programa=self.codigo_programa).all()]

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

class ComentarioBolsista(db.Model):
    """
    Tabela: comentarios_bolsista
    Descrição: Histórico de anotações para o bolsista.
    """
    __tablename__ = 'comentarios_bolsista'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=utc_now)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    # Relacionamentos
    bolsista = db.relationship('Bolsista', back_populates='comentarios_historico')
    autor = db.relationship('User')

class ComentarioEdital(db.Model):
    """
    Tabela: comentarios_edital
    Descrição: Histórico de anotações para o edital.
    """
    __tablename__ = 'comentarios_edital'

    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=utc_now)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    edital = db.relationship('Edital', back_populates='comentarios_historico')
    autor = db.relationship('User')

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

    # [NEW] V5.2 Link: Vínculo Direto com Campus (Normalização NAPI)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=True)
    campus = db.relationship('Campus', foreign_keys=[campus_id])

    # Dados Pessoais
    nome = db.Column(db.String(100), nullable=False)
    registro_academico = db.Column(db.String(20), nullable=True) # Matrícula/RA desacoplada de unicidade sistêmica
    matricula = db.Column(db.String(20), index=True)            # [NEW V10.8] Identidade Institucional
    # [V16] CPF não é mais único para permitir múltiplos vínculos históricos.
    # Regra de Negócio: Apenas UM registro por CPF pode ter ativo=True.
    # Isso permite que um discente migre de nível (M->D) ou troque de edital.
    cpf = db.Column(EncryptedString(255))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(30))
    data_nascimento = db.Column(db.Date, nullable=True)
    pais_origem = db.Column(db.String(100), default='Brasil') # [NEW Phase 2 - Internacionalização]
    
    # Dados Acadêmicos
    orientador = db.Column(db.String(100))
    email_orientador = db.Column(db.String(100)) # [NEW] V2
    
    # [NEW] NAPI-Robótica Externos (Legado pós-V5 será substituído por campus_id)
    cidade = db.Column(db.String(100))
    instituicao = db.Column(db.String(150))
    
    # [PROPERTY] get_origem: Retorna a origem institucional padronizada
    @property
    def get_origem(self):
        if self.campus:
            return f"{self.campus.instituicao} - {self.campus.nome}"
        elif self.programa_link and self.programa_link.campus:
            return f"{self.programa_link.campus.instituicao} - {self.programa_link.campus.nome}"
        elif self.instituicao:
            if self.cidade:
                return f"{self.instituicao} ({self.cidade})"
            return self.instituicao
        return "Não Informado"
    
    # [PROPERTY] get_instituicao: Retorna apenas a instituição de origem sem duplicar
    @property
    def get_instituicao(self):
        if self.instituicao and self.instituicao.strip():
            return self.instituicao.strip()
        if self.campus:
            return self.campus.instituicao or "UTFPR"
        if self.programa_link and self.programa_link.campus:
            return self.programa_link.campus.instituicao or "UTFPR"
        return "Não Informada"

    @property
    def sigla_campus_display(self):
        if self.programa_link and self.programa_link.campus:
            return self.programa_link.campus.sigla_campus
        if self.campus:
            return self.campus.sigla_campus
        return None
    
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
    
    # [NEW] NAPI-Robótica (Restored for compatibility with blueprints/templates)
    projeto_pesquisa = db.Column(db.String(255))
    agencia_fomento = db.Column(db.String(100))
    recebe_bolsa = db.Column(db.Boolean, default=True)
    
    is_pdse = db.Column(db.Boolean, default=False) # [NEW] V3: Flag para Sanduíche
    pais_destino = db.Column(db.String(100))       # [NEW] V3: País do Sanduíche
    
    data_inicio_bolsa = db.Column(db.Date)
    meses_duracao = db.Column(db.Integer)
    data_fim_bolsa = db.Column(db.Date) # Calculada automaticamente
    
    # Status e Desligamento
    ativo = db.Column(db.Boolean, default=True)
    # Cadastrado sem pagamentos: aguarda vigência e/ou contrato FUNTEF/FA
    implantacao_pendente = db.Column(db.Boolean, default=False)
    motivo_desligamento = db.Column(db.Text)
    data_desligamento = db.Column(db.Date)
    
    # [NEW FASE 5] Monitoramento de Devolução
    devolucao_valores = db.Column(db.Boolean, default=False)

    # [NEW GOVERNANÇA NAPI-ROBÓTICA] PI 33/2026
    status_governanca = db.Column(db.String(20), default='PENDENTE') # PENDENTE, ATIVO, INATIVO
    data_liberacao_fundacao = db.Column(db.Date, nullable=True) # Data informada pela Fundação Araucária

    
    # [NEW] Backup da data de fim para toggle ativo/inativo
    data_fim_bolsa_backup = db.Column(db.Date)  # Armazena data_fim_bolsa original ao desativar
    
    # [NEW] Cotas/Parcelas Adicionais
    tem_adicional = db.Column(db.Boolean, default=False)
    valor_adicional = db.Column(db.Numeric(12, 2), default=0.0) # Valor UNITÁRIO da parcela adicional
    qtd_adicional = db.Column(db.Integer, default=1)   # Quantidade de parcelas adicionais
    
    # [NEW PHASE 2] Controle de Checkout/Relatório Final
    relatorio_entregue = db.Column(db.Boolean, default=False)
    relatorio_ultima_cobranca_em = db.Column(db.DateTime, nullable=True)

    # [FUNTEF / Conveniar] Onboarding de novo bolsista
    link_pasta_nuvem = db.Column(db.Text)
    conveniar_cadastrado = db.Column(db.Boolean, default=False)
    funtef_email_enviado_em = db.Column(db.DateTime, nullable=True)
    funtef_contrato_pronto = db.Column(db.Boolean, default=False)

    # [AVISO ÚLTIMO MÊS] Notificação proativa ao bolsista e orientador
    ultimo_mes_email_enviado_em = db.Column(db.DateTime, nullable=True)
    ultimo_mes_email_competencia = db.Column(db.String(7), nullable=True)  # YYYY-MM

    # Confirmação de início (bolsista + orientador, após ativação FA)
    inicio_email_enviado_em = db.Column(db.DateTime, nullable=True)

    # [NEW FASE 4] Índices Estratégicos para Performance
    # Aceleram consultas frequentes (listagens, dashboards, filtros)
    __table_args__ = (
        db.Index('idx_bolsistas_ativo', 'ativo'),           # Filtro Ativo vs Inativo
        db.Index('idx_bolsistas_edital', 'edital_id'),     # Bolsistas por Edital
        db.Index('idx_bolsistas_programa', 'programa_id'), # Bolsistas por Programa
    )

    def check_status_validity(self):
        """
        [V11.8] Calcula o status dinâmico delegando à StatusEngine (State Pattern).
        """
        from core.status_engine import StatusEngine
        return StatusEngine.get_status(self)

    @property
    def em_ultimo_mes_bolsa(self):
        """True se ativo e data_fim_bolsa cai no mês/ano corrente."""
        from datetime import date
        hoje = date.today()
        return bool(
            self.ativo
            and self.data_fim_bolsa
            and self.data_fim_bolsa.month == hoje.month
            and self.data_fim_bolsa.year == hoje.year
        )

    @property
    def pendencias_implantacao(self):
        from services.implantacao_bolsa_service import ImplantacaoBolsaService
        return ImplantacaoBolsaService.pendencias(self, exigir_inicio=False)

    @property
    def motivo_implantacao_pendente(self):
        from services.implantacao_bolsa_service import ImplantacaoBolsaService
        return ImplantacaoBolsaService.label_pendencia(self)

    @property
    def cobranca_relatorio_pendente(self):
        """Desligado sem checkout de relatório final (não inclui implantação pendente)."""
        return (
            (not self.ativo)
            and (not self.relatorio_entregue)
            and (not getattr(self, 'implantacao_pendente', False))
            and getattr(self, 'status_governanca', None) != 'PENDENTE'
        )
    
    def update_governance_status(self):
        """
        [V13.0] Sincroniza o status_governanca com o resultado do StatusEngine.
        Foco no PI 33/2026.
        """
        current_status = self.check_status_validity()
        from core.status_engine import BolsistaStatus
        
        if current_status == BolsistaStatus.INATIVO:
            self.status_governanca = 'INATIVO'
        elif current_status in (
            BolsistaStatus.PENDENTE_GOVERNANCA,
            BolsistaStatus.AGUARDANDO_IMPLANTACAO,
        ):
             self.status_governanca = 'PENDENTE'
        else:
            self.status_governanca = 'ATIVO'
        return self.status_governanca

    def apply_extension(self, months):
        """
        [V13.0] Aplica extensão na data_fim_bolsa devido a afastamento.
        """
        if not self.data_fim_bolsa: return
        from dateutil.relativedelta import relativedelta
        self.data_fim_bolsa += relativedelta(months=months)
        return self.data_fim_bolsa

    def revert_extension(self, months):
        """
        [V13.0] Reverte extensão na data_fim_bolsa.
        """
        if not self.data_fim_bolsa: return
        from dateutil.relativedelta import relativedelta
        self.data_fim_bolsa -= relativedelta(months=months)
        return self.data_fim_bolsa

    def get_status_display(self):
        """
        [V12.0] Retorna os metadados de exibição (label, cor, bg) do status.
        """
        from core.status_engine import StatusEngine
        status = self.check_status_validity()
        return StatusEngine.get_display_data(status)
    
    def create_snapshot(self, contexto="Alteração Manual"):
        """
        [V11.8] Captura o estado atual do bolsista para o Memento Pattern.
        """
        import json
        payload_data = {
            "nome": str(self.nome) if self.nome else "",
            "data_inicio_bolsa": self.data_inicio_bolsa.strftime('%Y-%m-%d') if self.data_inicio_bolsa else None,
            "meses_duracao": int(self.meses_duracao) if self.meses_duracao else 0,
            "data_fim_bolsa": self.data_fim_bolsa.strftime('%Y-%m-%d') if self.data_fim_bolsa else None,
            "ativo": bool(self.ativo),
            "status_governanca": self.status_governanca,
            "data_liberacao_fundacao": self.data_liberacao_fundacao.strftime('%Y-%m-%d') if self.data_liberacao_fundacao else None,
            "motivo_desligamento": str(self.motivo_desligamento) if self.motivo_desligamento else None,
        }
        snapshot = BolsistaSnapshot(
            bolsista_id=self.id,
            contexto=str(contexto),
            data_fim_original=self.data_fim_bolsa,
            ativo_original=self.ativo,
            status_governanca_original=self.status_governanca,
            data_liberacao_original=self.data_liberacao_fundacao,
            payload=json.dumps(payload_data)
        )
        db.session.add(snapshot)
        return snapshot
    
    # Relacionamentos Inversos (back_populates)
    # foreign_keys explícitos para resolver ambiguidade caso existam múltiplos relacionamentos
    acompanhamentos = db.relationship('Acompanhamento', back_populates='bolsista', foreign_keys=[Acompanhamento.bolsista_id], cascade='all, delete-orphan', lazy=True)
    afastamentos = db.relationship('Afastamento', back_populates='bolsista', foreign_keys=[Afastamento.bolsista_id], cascade='all, delete-orphan', lazy=True)
    comentarios_historico = db.relationship('ComentarioBolsista', back_populates='bolsista', cascade='all, delete-orphan', lazy=True, order_by='desc(ComentarioBolsista.criado_em)')


class Residente(db.Model):
    """
    Tabela: residentes
    Descrição: Armazena dados dos residentes pós-doutorais.
    Separado de Bolsistas para permitir ciclo de vida independente.
    """
    __tablename__ = 'residentes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Vínculo Institucional
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id', ondelete='SET NULL'), nullable=True)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades.id', ondelete='SET NULL'), nullable=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True)
    
    # Relacionamentos
    edital = db.relationship('Edital', backref=db.backref('residentes', lazy=True))
    modalidade = db.relationship('Modalidade', backref=db.backref('residentes', lazy=True))
    programa_link = db.relationship('ProgramaAcademico', backref=db.backref('residentes', lazy=True))

    # Dados Pessoais
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(EncryptedString(255))
    email = db.Column(db.String(100))
    
    # Dados Específicos Pós-Doc
    supervisor = db.Column(db.String(100))
    projeto_pesquisa = db.Column(db.String(255)) 
    agencia_fomento = db.Column(db.String(100))  
    recebe_bolsa = db.Column(db.Boolean, default=True)

    # Dados da Bolsa/Vigência
    processo_sei = db.Column(db.String(50))
    numero_formulario = db.Column(db.String(50))
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    meses_duracao = db.Column(db.Integer)

    # Cotas/Parcelas Adicionais
    tem_adicional = db.Column(db.Boolean, default=False)
    valor_adicional = db.Column(db.Numeric(12, 2), default=0.0)
    qtd_adicional = db.Column(db.Integer, default=1)
    
    # Valor Personalizado da Bolsa (Opcional)
    valor_bolsa = db.Column(db.Numeric(12, 2), nullable=True)

    # Status
    ativo = db.Column(db.Boolean, default=True)
    
    def check_status_validity(self):
        from datetime import date
        hoje = date.today()
        if not self.ativo: return 'INATIVO'
        if self.data_fim < hoje: return 'INATIVO'
        return 'ATIVO'

    def __repr__(self):
        return f"<Residente {self.nome} - {self.cpf}>"

class RodadaSelecao(db.Model):
    """
    Tabela: rodadas_selecao
    Descrição: Representa um ciclo de seleção dentro de um Edital.
    """
    __tablename__ = 'rodadas_selecao'
    
    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id'), nullable=False)
    
    nome = db.Column(db.String(100), nullable=False) # Ex: "Chamada Regular"
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    ativa = db.Column(db.Boolean, default=True)      # Se é a chamada atual
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, default=0)
    
    # Relações
    etapas = db.relationship('EtapaCronograma', backref='rodada', cascade='all, delete-orphan', lazy=True)
    candidaturas = db.relationship('Candidatura', backref='rodada', cascade='all, delete-orphan', lazy=True, order_by='Candidatura.ordem')

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
    Descrição: Registro de interessados na bolsa.
    """
    __tablename__ = 'candidaturas'
    
    id = db.Column(db.Integer, primary_key=True)
    rodada_id = db.Column(db.Integer, db.ForeignKey('rodadas_selecao.id'), nullable=False)
    ordem = db.Column(db.Integer, default=0)
    
    # Dados do Candidato
    nome = db.Column(db.String(100), nullable=False)
    registro_academico = db.Column(db.String(20), nullable=True)
    cpf = db.Column(EncryptedString(255))
    email = db.Column(db.String(100))
    
    # [NEW V10] Dados do Projeto/Orientação
    orientador = db.Column(db.String(100))
    email_orientador = db.Column(db.String(100))
    projeto_pesquisa = db.Column(db.String(255))
    
    # Dados Acadêmicos (Alvo)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('programa_academico.id'), nullable=True)
    
    # [NEW] NAPI-Robótica Externos
    cidade = db.Column(db.String(100))
    instituicao = db.Column(db.String(150))
    
    # Controle
    numero_sei = db.Column(db.String(50))
    numero_formulario = db.Column(db.String(50))
    anotacoes = db.Column(db.Text)
    
    # Status do Funil
    status = db.Column(db.String(20), default='INSCRITO') 
    
    data_submissao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campus = db.relationship('Campus')
    programa = db.relationship('ProgramaAcademico')

    @property
    def get_origem(self):
        if self.campus:
            return f"UTFPR - {self.campus.nome}"
        elif self.instituicao:
            return f"{self.instituicao} ({self.cidade})"
        return "Não Informado"

    # [PROPERTY] get_instituicao: Retorna apenas a instituição de origem sem duplicar
    @property
    def get_instituicao(self):
        if self.instituicao and self.instituicao.strip():
            return self.instituicao.strip()
        if self.campus:
            return self.campus.instituicao or "UTFPR"
        return "Não Informada"

# ============================================================================
# MÓDULO DE DADOS SOCIOECONÔMICOS E ÉTNICO-RACIAIS (FASE 20)
# ============================================================================

class DadosSociais(db.Model):
    """
    Tabela: dados_sociais
    Descrição: Armazena autodeclaração de raça, gênero e condições socioeconômicas.
    Relacionamento 1:1 com a tabela Bolsista.
    Objetivo: Embasar políticas de Ações Afirmativas e Permanência.
    """
    __tablename__ = 'dados_sociais'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id'), nullable=False, unique=True)
    
    # BLOCO 1: Identificação Étnico-Racial e Gênero
    raca_cor = db.Column(db.String(50))           # Branca, Preta, Parda, Amarela, Indígena
    genero_identidade = db.Column(db.String(50))  # Mulher Cis/Trans, Homem Cis/Trans, Não-binário
    orientacao_sexual = db.Column(db.String(50))  # [NEW] Hetero, Homo, Bi, Outros, Prefere não declarar
    pcd = db.Column(db.Boolean, default=False)
    pcd_detalhe = db.Column(db.String(255))       # Especificação da deficiência
    
    # BLOCO 2: Povos Indígenas e Comunidades Tradicionais
    etnia_origem = db.Column(db.String(100))      # Ex: Kaingang
    vinculo_comunidade = db.Column(db.String(100))# Reside na terra / Reside fora
    lingua_materna = db.Column(db.String(100))    # Para apoio linguístico
    is_quilombola = db.Column(db.Boolean, default=False)  # [NEW] Autodeclaração quilombola
    comunidade_quilombola = db.Column(db.String(150))     # [NEW] Nome da comunidade
    
    # BLOCO 2B: Internacionalização e Dados Humanitários (Refugiados) [PLANEJAMENTO 2026]
    is_refugiado = db.Column(db.Boolean, default=False)   # [NEW 2026] Indica se é refugiado ou solicitante
    pais_origem_refugio = db.Column(db.String(100))       # [NEW 2026] País de origem (para refugiados)
    status_legal_refugio = db.Column(db.String(50))       # [NEW 2026] Solicitante de Refúgio, Refugiado Reconhecido, Visto Humanitário
    idioma_materno = db.Column(db.String(100))            # [NEW 2026] Idioma nativo para apoio linguístico
    necessidades_especificas = db.Column(db.Text)         # [NEW 2026] Apoio psicológico, moradia, validação de diploma, etc.
    
    # BLOCO 3: Trajetória Educacional e Socioeconômica
    ensino_medio_origem = db.Column(db.String(100)) # Pública, Privada c/ Bolsa, Privada s/ Bolsa
    cotista_anterior = db.Column(db.Boolean)
    renda_per_capita = db.Column(db.String(50))   # Faixas em salários mínimos
    primeira_geracao_superior = db.Column(db.Boolean, default=False)  # [NEW] Primeiro da família na graduação
    
    # BLOCO 4: Indicadores de Permanência
    fonte_renda = db.Column(db.String(100))       # Trabalho, Família, Bolsa
    possui_dependentes = db.Column(db.Boolean)
    situacao_moradia = db.Column(db.String(100))  # Própria, Alugada, Casa Estudante
    
    # Metadados
    criado_em = db.Column(db.DateTime, default=utc_now)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    # Relacionamento 1:1
    bolsista = db.relationship('Bolsista', backref=db.backref('dados_sociais', uselist=False, cascade='all, delete-orphan'))

class AuditLog(db.Model):

    """
    Tabela: auditoria_logs
    Descrição: Registro de segurança de ações críticas no sistema.
    """
    __tablename__ = 'auditoria_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    acao = db.Column(db.String(50), nullable=False)
    tabela = db.Column(db.String(50))
    registro_id = db.Column(db.String(50))
    detalhes = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    data_hora = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))


# [Fase 9] Módulo de Internacionalização
class MobilidadeInternacional(db.Model):
    """
    Tabela: mobilidade_internacional
    Descrição: Registro de períodos de mobilidade (Sanduíche, Estágio, Dupla Diplomação).
    """
    __tablename__ = 'mobilidade_internacional'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id'), nullable=False)
    
    # [NEW] Vínculo com Acordos Internacionais
    acordo_id = db.Column(db.Integer, db.ForeignKey('acordos_internacionais.id', ondelete='SET NULL'), nullable=True)
    
    pais_destino = db.Column(db.String(100), nullable=False)
    instituicao_destino = db.Column(db.String(200), nullable=False)
    
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    

    
    tipo_fluxo = db.Column(db.String(20), default='saida') # 'saida' (Outbound), 'entrada' (Inbound)
    tipo_mobilidade = db.Column(db.String(100)) # Ex: Doutorado Sanduíche, Cotutela
    agencia_fomento = db.Column(db.String(100)) # Ex: CAPES-PrInt, CNPq, Próprio
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    bolsista = db.relationship('Bolsista', backref=db.backref('mobilidades', lazy=True, cascade='all, delete-orphan'))
    acordo = db.relationship('AcordoInternacional', backref='mobilidades_vinculadas')

class AcordoInternacional(db.Model):
    """
    Tabela: acordos_internacionais
    Descrição: Registro formal de parcerias entre a UTFPR e instituições estrangeiras.
    """
    __tablename__ = 'acordos_internacionais'
    
    id = db.Column(db.Integer, primary_key=True)
    pais = db.Column(db.String(100), nullable=False, index=True)
    instituicao = db.Column(db.String(255), nullable=False)
    processo_sei = db.Column(db.String(50))
    tipo_acordo = db.Column(db.String(100)) # Ex: Dupla Diplomação, Cooperação Técnica
    data_assinatura = db.Column(db.Date)
    data_vencimento = db.Column(db.Date)
    vagas_anuais = db.Column(db.Integer, default=0)
    idioma_instrucao = db.Column(db.String(100))
    areas_conhecimento = db.Column(db.Text) # Áreas dos PPGs abrangidas
    ativo = db.Column(db.Boolean, default=True)
    is_gcub = db.Column(db.Boolean, default=False, index=True) # Indica se pertence ao GCUB
    numero_edital = db.Column(db.String(100), nullable=True, index=True) # Edital vinculado
    
    # Metadados para auditoria
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pais": self.pais,
            "instituicao": self.instituicao,
            "processo_sei": self.processo_sei or '',
            "tipo": self.tipo_acordo,
            "data_assinatura": self.data_assinatura.strftime('%Y-%m-%d') if self.data_assinatura else '',
            "data_vencimento": self.data_vencimento.strftime('%Y-%m-%d') if self.data_vencimento else '',
            "vagas_anuais": self.vagas_anuais or 0,
            "idioma_instrucao": self.idioma_instrucao or '',
            "areas_conhecimento": self.areas_conhecimento or '',
            "status": "Ativo" if self.ativo else "Inativo",
            "is_gcub": self.is_gcub,
            "numero_edital": self.numero_edital or ''
        }

class SistemaConfig(db.Model):
    """Configurações editáveis pelo admin (chave/valor)."""
    __tablename__ = 'sistema_config'

    chave = db.Column(db.String(100), primary_key=True)
    valor = db.Column(db.Text)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class AnotacaoSistema(db.Model):
    """
    Tabela: anotacoes_sistema
    Quadro de tarefas compartilhado da equipe NAPI-Robótica.
    """
    __tablename__ = 'anotacoes_sistema'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    texto = db.Column(db.Text, nullable=False)
    concluida = db.Column(db.Boolean, default=False, nullable=False)
    concluida_em = db.Column(db.DateTime, nullable=True)
    criado_em = db.Column(db.DateTime, default=utc_now)
    atualizado_em = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    autor = db.relationship('User', backref=db.backref('anotacoes_sistema', lazy=True))


class LogAutomacao(db.Model):
    """
    Entidade de Observabilidade: Registra o sucesso ou falha 
    de tarefas agendadas e rotinas de backend.
    """
    __tablename__ = 'logs_automacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_tarefa = db.Column(db.String(100), nullable=False) # Ex: "Relatório Semanal Excel"
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False) # 'SUCESSO' ou 'ERRO'
    mensagem = db.Column(db.Text) # Descrição do erro ou resumo da execução
    registros_processados = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<LogAutomacao {self.nome_tarefa} - {self.status}>'

# ============================================================================
# MÓDULO DE SEGURANÇA E RECUPERAÇÃO (Snapshot/Memento) [V10.8]
# ============================================================================

class DatabaseMemento(db.Model):
    """
    Tabela: database_mementos
    Descrição: Armazena snapshots de estado do banco antes de importações massivas.
    Utiliza JSONB (PostgreSQL) para flexibilidade e performance.
    """
    __tablename__ = 'database_mementos'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    contexto = db.Column(db.String(255), nullable=False)
    snapshot_data = db.Column(JSONB, nullable=False)
    total_registros = db.Column(db.Integer)
    checksum = db.Column(db.String(64))

    def __repr__(self):
        return f'<DatabaseMemento {self.contexto} em {self.timestamp}>'

class BolsistaSnapshot(db.Model):
    """
    Tabela: bolsista_snapshots
    Descrição: Memento Pattern para um único bolsista. 
    Permite auditoria granular e reversão de alterações estruturais.
    """
    __tablename__ = 'bolsista_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsistas.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    contexto = db.Column(db.String(200))
    
    # Estados Críticos para comparação rápida
    data_fim_original = db.Column(db.Date)
    ativo_original = db.Column(db.Boolean)
    status_governanca_original = db.Column(db.String(20))
    data_liberacao_original = db.Column(db.Date)
    
    # Payload completo serializado
    payload = db.Column(db.Text)
    
    # Relacionamento
    bolsista = db.relationship('Bolsista', backref=db.backref('snapshots', cascade='all, delete-orphan', order_by='BolsistaSnapshot.timestamp.desc()'))

# ============================================================================
# MÓDULO DE INTERFACE DINÂMICA (UI Memento) [V11.1]
# ============================================================================

class UIState(db.Model):
    """
    Tabela: ui_state
    Descrição: Armazena o estado atual (textos) dos elementos da interface.
    Permite edição visual direta sem alteração de código.
    """
    __tablename__ = 'ui_state'
    
    id = db.Column(db.Integer, primary_key=True)
    element_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    current_text = db.Column(db.Text, nullable=False)
    page_context = db.Column(db.String(100)) # Ex: "sidebar", "dashboard"
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UIState {self.element_key}: {self.current_text[:20]}...>'

class UIMementoHistory(db.Model):
    """
    Tabela: ui_memento_history
    Descrição: Padrão Memento para a Interface do Usuário.
    Armazena snapshots completos da tabela ui_state para restauração segura.
    """
    __tablename__ = 'ui_memento_history'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    description = db.Column(db.Text)
    
    # Snapshot completo em JSONB: { element_key: current_text }
    ui_snapshot = db.Column(JSONB, nullable=False)
    
    # Relacionamento com quem fez a alteração
    user = db.relationship('User', backref=db.backref('ui_mementos', lazy=True))

    def __repr__(self):
        return f'<UIMementoHistory snapshot em {self.timestamp}>'

# --- LISTENERS DE VALIDAÇÃO ATÔMICA ---

@event.listens_for(AcordoInternacional, 'before_insert')
@event.listens_for(AcordoInternacional, 'before_update')
def validar_acordo_gcub(mapper, connection, target):
    """
    Garante que acordos GCUB sempre possuam número de edital.
    Executado antes da persistência para evitar problemas de ordem de atribuição.
    """
    if target.is_gcub and not target.numero_edital:
        raise ValueError("O número do edital é obrigatório para acordos GCUB.")
