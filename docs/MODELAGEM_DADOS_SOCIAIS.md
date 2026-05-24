# Especificação Técnica: Modelagem de Dados Sociais (V7)

Este documento detalha a estrutura de banco de dados necessária para suportar o **Plano de Expansão Socioeconômica**, utilizando SQLAlchemy (ORM).

---

## 1. Visão Geral do Schema

A estratégia é utilizar uma tabela satélite (`social_profile`) com relacionamento **1:1** com a tabela principal `bolsistas`. Isso permite:
1.  **Segurança:** Isolar dados sensíveis em uma tabela que pode ter regras de acesso mais estritas.
2.  **Organização:** Não poluir a tabela `bolsistas` (que já é complexa) com mais 20 campos.
3.  **Opcionalidade:** O preenchimento é facultativo sem afetar a integridade do cadastro principal.

---

## 2. Código do Modelo (SQLAlchemy)

```python
from enum import Enum
from app import db  # Assumindo a instância db do Flask-SQLAlchemy

# --- Enums Padronizados (IBGE/Sucupira) ---

class RacaCor(Enum):
    BRANCA = "Branca"
    PRETA = "Preta"
    PARDA = "Parda"
    AMARELA = "Amarela"
    INDIGENA = "Indígena"
    NAO_DECLARADO = "Não declarado"

class GeneroIdentidade(Enum):
    CISGENERO = "Cisgênero"
    TRANSGENERO = "Transgênero"
    NAO_BINARIO = "Não-binário"
    OUTRO = "Outro"
    PREFIRO_NAO_DIZER = "Prefiro não dizer"

class FaixaRenda(Enum):
    # Baseado em Salários Mínimos (SM)
    ATE_1_5 = "Até 1,5 SM"
    DE_1_5_A_3 = "De 1,5 a 3 SM"
    DE_3_A_5 = "De 3 a 5 SM"
    ACIMA_5 = "Acima de 5 SM"

class OrigemEscolar(Enum):
    PUBLICA_INTEGRAL = "Escola Pública (Integral)"
    PUBLICA_PARCIAL = "Escola Pública (Parcial)"
    PRIVADA_COM_BOLSA = "Privada (Com Bolsa)"
    PRIVADA_SEM_BOLSA = "Privada (Integral)"

# --- Tabela Satélite ---

class PerfilSocioeconomico(db.Model):
    __tablename__ = 'perfil_socioeconomico'

    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamento 1:1 com Bolsista
    bolsista_id = db.Column(db.Integer, db.ForeignKey('bolsitas.id'), unique=True, nullable=False)
    
    # 1. Identidade (Dados Sensíveis - Proteção Alta)
    raca_cor = db.Column(db.Enum(RacaCor), nullable=True)
    genero_identidade = db.Column(db.Enum(GeneroIdentidade), nullable=True)
    
    # PCD (Pessoa com Deficiência)
    is_pcd = db.Column(db.Boolean, default=False)
    detalhe_deficiencia = db.Column(db.String(100), nullable=True) # Ex: Auditiva, Motora (Opcional)
    
    # 2. Contexto Econômico
    faixa_renda_familiar = db.Column(db.Enum(FaixaRenda), nullable=True)
    possui_vinculo_empregaticio = db.Column(db.Boolean, default=False)
    qtde_dependentes_economia = db.Column(db.Integer, default=0) # Quantas pessoas dependem da renda
    
    # 3. Histórico e Mobilidade
    origem_escolar_medio = db.Column(db.Enum(OrigemEscolar), nullable=True)
    primeira_geracao_superior = db.Column(db.Boolean, default=False) # Primeiro da família na faculdade?
    primeira_geracao_pos = db.Column(db.Boolean, default=False)      # Primeiro da família na Pós?
    
    # 4. Maternidade/Paternidade (Ações Afirmativas)
    possui_filhos = db.Column(db.Boolean, default=False)
    idade_filho_cacula = db.Column(db.Integer, nullable=True) # Relevante para auxílio creche/prioridade
    
    # Metadados
    data_atualizacao = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    consentimento_lgpd_versao = db.Column(db.String(10), default="v1.0") # Rastreabilidade do aceite

    # Backref para acesso fácil: bolsista.perfil_social
    bolsista = db.relationship("Bolsista", backref=db.backref("perfil_social", uselist=False))

    def __repr__(self):
        return f"<PerfilSocial BolsistaID={self.bolsista_id}>"
```

## 3. SQL de Migração (Exemplo SQLite)

Se fôssemos aplicar isso manualmente sem Alembic:

```sql
CREATE TABLE perfil_socioeconomico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bolsista_id INTEGER NOT NULL UNIQUE,
    raca_cor VARCHAR(20),
    genero_identidade VARCHAR(20),
    is_pcd BOOLEAN DEFAULT 0,
    detalhe_deficiencia VARCHAR(100),
    faixa_renda_familiar VARCHAR(20),
    possui_vinculo_empregaticio BOOLEAN DEFAULT 0,
    origem_escolar_medio VARCHAR(30),
    primeira_geracao_superior BOOLEAN DEFAULT 0,
    primeira_geracao_pos BOOLEAN DEFAULT 0,
    possui_filhos BOOLEAN DEFAULT 0,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consentimento_lgpd_versao VARCHAR(10),
    FOREIGN KEY(bolsista_id) REFERENCES bolsistas(id) ON DELETE CASCADE
);
```

## 4. Estratégia de Implementação na Interface

1.  **Formulário:** Adicionar uma nova "Tab" no cadastro do bolsista chamada "Perfil Social".
2.  **Disclaimer:** Incluir aviso claro: *"Estes dados são utilizados exclusivamente para fins estatísticos e de formulação de políticas de permanência, conforme Lei Geral de Proteção de Dados."*
3.  **Botão "Não desejo declarar":** Todos os campos devem ser opcionais ou ter essa opção explicita.

---
*HaruLabs Tech Specs*
