# Plano de Implementação: Gestão de Etapas e Múltiplas Rodadas (V8)

**Objetivo:** Permitir que um Edital tenha múltiplos ciclos (rodadas) de seleção independentes, gerenciando cronogramas específicos para cada fase (submissão, análise, resultados), vital para preenchimento de vagas ociosas.

---

## 1. Nova Modelagem de Dados

Atualmente o `Edital` é monolítico. A nova estrutura propõe uma hierarquia: `Edital -> RodadaSelecao -> EtapaCronograma`.

### A. Tabela `RodadaSelecao` (Selection Rounds)
Representa um ciclo completo de seleção. Ex: "Chamada Regular", "Chamada Bolsas Remanescentes".

```python
class RodadaSelecao(db.Model):
    __tablename__ = 'rodadas_selecao'
    
    id = db.Column(db.Integer, primary_key=True)
    edital_id = db.Column(db.Integer, db.ForeignKey('editais.id'), nullable=False)
    
    # Ex: "1ª Chamada", "Processo Seletivo Complementar"
    nome = db.Column(db.String(100), nullable=False)
    
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    
    # Status: 'ABERTA', 'EM_ANALISE', 'FINALIZADA', 'CANCELADA'
    status = db.Column(db.String(20), default='ABERTA')
    
    # Relacionamento com Edital
    edital = db.relationship('Edital', backref=db.backref('rodadas', cascade='all, delete-orphan'))
```

### B. Tabela `EtapaCronograma` (Timeline)
Detalha as fases dentro de uma rodada específica.

```python
class EtapaCronograma(db.Model):
    __tablename__ = 'etapas_cronograma'
    
    id = db.Column(db.Integer, primary_key=True)
    rodada_id = db.Column(db.Integer, db.ForeignKey('rodadas_selecao.id'), nullable=False)
    
    titulo = db.Column(db.String(100), nullable=False) # Ex: "Inscrição", "Resultado Preliminar"
    descricao = db.Column(db.Text)
    
    data_limite = db.Column(db.DateTime, nullable=False)
    
    ordem_exibicao = db.Column(db.Integer, default=0) # Para ordenar na UI
    concluida = db.Column(db.Boolean, default=False)
    
    rodada = db.relationship('RodadaSelecao', backref=db.backref('etapas', cascade='all, delete-orphan'))
```

---

## 2. Experiência do Usuário (UX/UI)

### Página de Detalhes do Edital (`/editais/<id>`)
Será adicionada uma nova seção ou aba "Ciclos de Seleção":

1.  **Visualização em Acordeão:** Cada Rodada é um bloco expansível.
    *   *Rodada 1 (Finalizada)* [Expandir]
    *   *Rodada 2 - Remanescentes (Em Andamento)* [Expandir]
2.  **Cronograma Visual:** Dentro de cada rodada, uma linha do tempo horizontal (Stepper) mostrando as etapas.
3.  **Botão de Ação:** 
    *   `[ + Nova Rodada ]`: Abre modal para criar um novo ciclo (Nome, Início, Fim).
    *   Ao criar, o sistema pode sugerir clonar as etapas da rodada anterior para agilizar.

### Página de Candidatos (`/editais/<id>/selecao`)
Os candidatos agora devem ser vinculados a uma **Rodada** específica.
*   Filtro Dropdown no topo: "Filtrar por: Todas as Rodadas | Rodada 1 | Rodada 2".

---

## 3. Lógica de Negócio (Vagas Ociosas)

Quando uma nova rodada é aberta:
1.  O sistema deve calcular o **Saldo de Vagas**: `Vagas Totais do Edital - Bolsistas Ativos (Todas as Rodadas)`.
2.  Exibir um alerta no dashboard da nova rodada: *"Este edital possui X vagas remanescentes disponíveis para esta chamada."*

---

## 4. Roteiro de Implementação

1.  **Backend:** Criar modelos e migrar banco (`flask db upgrade`).
2.  **Frontend:** Atualizar `templates/editais/detalhes.html` para listar rodadas.
3.  **Funcionalidade:** Implementar rotas para CRUD de Rodadas e Etapas.
4.  **Integração:** Vincular novos candidatos à rodada ativa no momento do cadastro.

---
*HaruLabs Engineering Plan*
