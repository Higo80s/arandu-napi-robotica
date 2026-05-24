# Estudo de Caso Avançado: Arquitetura, Banco de Dados e Engenharia de Software
**Projeto:** Sistema de Gestão de Editais
**Público-Alvo:** Estudantes de Análise e Desenvolvimento de Sistemas (ADS), Engenharia de Software e Ciência da Computação.
**Versão do Estudo:** 2.2 (Inclusão do Dicionário de Dados - V7.0)

---

## 1. Contextualização e Motivação

### 1.1 O Cenário Real
Muitos estudantes perguntam: *"Por que não posso usar Excel para tudo?"*
Antes deste software, a gestão de bolsas era realizada justamente através de planilhas desconexas. Isso gerava três problemas críticos que nenhum banco de dados aceitaria:

1.  **Redundância de Dados:** O mesmo aluno era cadastrado 3 vezes se tivesse 3 bolsas diferentes. Se ele mudasse de telefone, era necessário atualizar em 3 lugares (anomalia de atualização).
2.  **Inconsistência:** O campo "Curso" recebia valores como "Eng. Mecânica", "Mecanica" e "Engenharia Mec". Isso tornava impossível agrupar dados para relatórios gerenciais.
3.  **Fragilidade (Falta de ACID):** Se a energia caísse durante uma edição, o arquivo poderia se corromper. Bancos de dados garantem que uma transação (cadastro) "ou acontece 100% ou não acontece nada".

---

## 2. Tecnologias: Análise da Stack

Para resolver esses problemas, selecionamos tecnologias baseadas em **produtividade** e **manutenibilidade**. Abaixo, detalhamos as escolhas:

### 2.1 Linguagem: Python 3
*   **Função:** Linguagem de Backend.
*   **Por que escolhemos?** Pela legibilidade ("Código é lido mais vezes do que é escrito"). A tipagem dinâmica acelera o desenvolvimento inicial.
*   **Trade-off:** Menor performance bruta que C++ ou Go, mas em sistemas administrativos (CRUD), o gargalo geralmente é o banco de dados, não a CPU.

### 2.2 Framework Web: Flask
*   **Função:** Receber requisições HTTP e devolver HTML.
*   **Por que escolhemos?** É um microframework. Diferente do Django (que já traz tudo pronto e rígido), o Flask permite montar a arquitetura peça por peça. Isso é excelente para aprendizado.
*   **Vantagem:** Extrema flexibilidade.
*   **Desvantagem:** Exige configurar conexões e autenticação manualmente.

### 2.3 Banco de Dados: SQLite
*   **Função:** Persistência de dados.
*   **Por que escolhemos?** É um banco *serverless* (um arquivo único `.db`).
*   **Vantagem:** Zero configuração ("Zero-conf"). Basta copiar o arquivo para fazer backup.
*   **Limitação:** Não suporta alta concorrência de escrita (bloqueia o arquivo todo). Ideal para até ~50 usuários simultâneos, o que atende perfeitamente nosso caso.

### 2.4 ORM: SQLAlchemy
*   **Função:** Mapeamento Objeto-Relacional.
*   **O que faz?** Permite manipular o banco usando Classes Python em vez de SQL puro.
*   **Benefício Estratégico:** Se no futuro precisarmos migrar para PostgreSQL (para suportar 1.000 usuários), mudamos apenas 1 linha de configuração. O código Python permanece igual.

---

## 3. Engenharia Reversa: O Banco de Dados (Schema)

A inteligência do sistema está nas **relações** entre as tabelas.

### 3.1 Diagrama Entidade-Relacionamento (Simplificado)

A estrutura segue uma hierarquia clara de dependência:

> **[EDITAL]**  --(possui)-->  **[MODALIDADE]**  --(financia)-->  **[BOLSISTA]**

Paralelamente, para normalizar os dados, temos tabelas auxiliares:

> **[CAMPUS]**  --(sedia)-->  **[PROGRAMA]**  --(vincula)-->  **[BOLSISTA]**

### 3.2 Análise Forense das Tabelas e Constraints

#### A. A Tabela `editais` (A Lei)
Representa o documento oficial.
*   **Constraint de Design:** Separação de responsabilidades. Se alterarmos o "Número do Edital", não precisamos varrer milhares de alunos para atualizar texto.

#### B. A Tabela `modalidades` (A Regra Financeira)
Define quanto paga cada nível (Mestrado = R$ 2.100, Doutorado = R$ 3.100).
*   **Engenharia de Segurança (`ON DELETE CASCADE`):** Esta tabela tem uma chave estrangeira para `editais` com a regra `CASCADE`.
    *   *O que isso faz?* Se um administrador excluir o Edital, o banco de dados (não o Python!) se encarrega de apagar imediatamente todas as modalidades filhas. Isso evita "lixo" no banco.

#### C. A Tabela `bolsistas` (O Beneficiário)
É a tabela central (Fato).
*   **Normalização V5.0:** Antigamente, o campo 'Programa' era digitado livremente. Agora, é um ID (`programa_id`) apontando para a tabela `programa_academico`. Isso garante integridade referencial.

#### D. A Tabela `residentes` (O Caso Especial V7.0)
Nesta versão, introduzimos uma decisão arquitetural importante. Pesquisadores de Pós-Doutorado não seguem as mesmas regras de alunos.
*   **O Problema:** Um Pós-Doc pode continuar vinculado à universidade mesmo se o edital de fomento acabar (como voluntário).
*   **A Solução (`ON DELETE SET NULL`):** Ao contrário dos bolsistas, a chave estrangeira do Residente usa `SET NULL`. Se apagarmos o Edital, o Residente **permanece** no banco, apenas com o campo `edital_id` vazio.

---

## 4. O Caminho do Dado: Desenvolvimento Full Stack

Para estudantes de ADS, é vital entender o ciclo de vida de uma requisição. Vamos rastrear o clique do botão "Salvar".

### Passo 1: O Cliente (Frontend)
O navegador envia um pacote HTTP POST.
*   **Arquivo:** `form.html`
*   **Ação:** O formulário coleta os dados e os empacota.

### Passo 2: O Controlador (Backend/Flask)
O servidor recebe o pacote e o Flask roteia para a função correta.
*   **Arquivo:** `app.py`
*   **Lógica:**
    1.  Recebe `request.form['nome']`.
    2.  Valida (ex: CPF é válido?).
    3.  Instancia um objeto da classe `Bolsista`.

### Passo 3: O Modelo (ORM)
A mágica acontece aqui. O SQLAlchemy traduz o objeto Python:
`novo_bolsista = Bolsista(nome="João")`
Para SQL nativo:
`INSERT INTO bolsistas (nome) VALUES ('João');`

### Passo 4: A Persistência (Disco)
O SQLite (driver) escreve os bits fisicamente no arquivo `.db`. Graças às transações, se o disco encher neste milissegundo, a operação é abortada inteiramente.

---

## 5. Dicionário de Dados Completo (Esquema Físico)

Abaixo descrevemos a estrutura exata das tabelas conforme implementadas (`Schema V7.0`).

### Tabela: `editais`
Armazena os documentos reguladores.
*   `id` (Integer): Chave Primária (PK). Autoincrementável.
*   `numero` (String 50): Obrigatório. Ex: '01/2024'.
*   `agencia` (String 50): Obrigatório. Ex: 'CNPq', 'CAPES'.
*   `processo_sei` (String 50): Opcional. Link para o processo administrativo.
*   `descricao` (String 200): Título ou resumo do edital.
*   `codigo_projeto` (String 50): Código interno institucional.
*   `descricao_projeto` (Text): Detalhamento do projeto.
*   `comentarios` (Text): Anotações internas.

### Tabela: `modalidades`
Regras financeiras vinculadas a um edital.
*   `id` (Integer): PK.
*   `edital_id` (Integer): FK -> `editais.id`. **Constraint:** `ON DELETE CASCADE`.
*   `nivel` (String 50): Obrigatório. Ex: 'Mestrado', 'Doutorado'.
*   `vagas` (Integer): Obrigatório. Quantidade total de cotas.
*   `valor_mensal` (Float): Obrigatório. Valor em Reais (R$).
*   `max_meses` (Integer): Duração máxima permitida.

### Tabela: `campus`
Tabela de Domínio (Normalização).
*   `id` (Integer): PK.
*   `nome` (String 100): Ex: 'Ponta Grossa'.
*   `sigla_campus` (String 10): Ex: 'PG'.

### Tabela: `programa_academico`
Cursos de Pós-Graduação (Normalização).
*   `id` (Integer): PK.
*   `campus_id` (Integer): FK -> `campus.id`.
*   `nome_programa` (String 200): Ex: 'Engenharia de Produção'.
*   `sigla_programa` (String 20): Ex: 'PPGEP'.
*   `codigo_programa` (String 50): Único. Código Sucupira/CAPES.

### Tabela: `bolsistas`
Tabela Fato (Alunos de Mestrado/Doutorado).
*   `id` (Integer): PK.
*   `edital_id` (Integer): FK -> `editais.id`.
*   `modalidade_id` (Integer): FK -> `modalidades.id`.
*   `programa_id` (Integer): FK -> `programa_academico.id`. Normalizado na V5.
*   `nome` (String 100): Obrigatório. Nome completo.
*   `cpf` (String 14): Único. Identificador nacional.
*   `email` (String 100): Contato.
*   `orientador` (String 100): Nome do professor responsável.
*   `data_inicio_bolsa` (Date): Obrigatório. Início do pagamento.
*   `meses_duracao` (Integer): Obrigatório. Tempo de vigência.
*   `data_fim_bolsa` (Date): Obrigatório. Calculado automaticamente (`Inicio + Meses`).
*   `ativo` (Boolean): Default=True. Define se aparece no relatório mensal.
*   `banco`, `agencia`, `conta`, `tipo_conta`: Dados financeiros.

### Tabela: `residentes` (Novo V7.0)
Tabela segregada para Pós-Doutorado.
*   `id` (Integer): PK.
*   `edital_id` (Integer): FK -> `editais.id`. **Constraint:** `ON DELETE SET NULL`.
*   `modalidade_id` (Integer): FK -> `modalidades.id`. **Constraint:** `ON DELETE SET NULL`.
*   `programa_id` (Integer): FK -> `programa_academico.id`.
*   `supervisor` (String 100): Professor supervisor do estágio pós-doutoral.
*   `projeto_pesquisa` (String 255): Título da pesquisa.
*   `agencia_fomento` (String 100): Fonte pagadora (pode diferir do Edital).
*   `recebe_bolsa` (Boolean): Indica se há fluxo financeiro ou é voluntário.

---

## 6. Desafios para o Futuro

Se você quiser praticar, tente desenhar soluções para estas evoluções:

1.  **Múltiplos Vínculos:** Hoje, um `Bolsista` tem apenas 1 `Modalidade`. Como você alteraria o banco para permitir que o mesmo aluno tenha 2 bolsas simultâneas? (Dica: Relação N:N ou Tabela de Vínculos).
2.  **Histórico Financeiro Real:** Crie uma tabela `Lancamentos` (1:N com Bolsista) contendo `Data`, `Valor` e `Tipo` (Pagamento/Estorno). Isso permitiria um extrato bancário real.
3.  **Sistema de Login (RBAC):** Implemente uma tabela `Usuarios` com perfis (`Role`). O coordenador pode ver tudo; o aluno só vê seus próprios dados. Isso exigiria Sessões e Hashing de senha.

---

**Conclusão Final**

Um sistema de software é um organismo vivo. Ele nasce simples e evolui conforme a complexidade do negócio aumenta. O segredo de um bom Arquiteto de Software não é saber todas as respostas, mas saber escolher as ferramentas (Constraints, ORMs, Frameworks) que tornam a evolução segura e sustentável.
