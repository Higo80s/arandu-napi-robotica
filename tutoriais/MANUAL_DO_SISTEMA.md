# MANUAL GLOBAL DO SISTEMA: GESTÃO DE EDITAIS

**Versão do Documento:** 1.0 (Referente ao Sistema V5.0)
**Data de Emissão:** 24 de Dezembro de 2025
**Responsável:** Equipe de Desenvolvimento (Assistente IA)
**Classificação:** Documentação Técnica e de Usuário

---

## 1. Apresentação
O **Gestão de Editais** é uma solução web desenvolvida para otimizar o controle administrativo e financeiro de bolsas acadêmicas. O sistema centraliza o ciclo de vida dos editais, desde a criação das modalidades até o pagamento e desligamento dos bolsistas.

---

## 2. Instalação e Configuração

### Pré-requisitos
*   Sistema Operacional: Windows 10/11.
*   Python 3.8 ou superior.

### Passo a Passo (Primeiro Uso)
1.  **Descompactar:** Extraia a pasta do projeto em local seguro (ex: `Meus Documentos`).
2.  **Ambiente Virtual:**
    *   Abra o terminal na pasta.
    *   Execute: `python -m venv .venv`
    *   Ative: `.\.venv\Scripts\activate`
3.  **Dependências:**
    *   Execute: `pip install -r requirements.txt`
4.  **Configuração (.env):**
    *   Copie `.env.example` para `.env`.
    *   Defina as senhas de segurança e banco de dados.

### Execução Diária
*   **Modo Usuário:** Clique no atalho `Gestao_Editais.bat` (Inicia o servidor em segundo plano e abre o navegador).
*   **Modo Adm/Dev:** Execute `python app.py` no terminal para ver logs detalhados.

---

## 3. Guia de Utilização

## 2. Acesso ao Sistema
O sistema é acessível via navegador web.

## 3. Painel Administrativo
### 3.1. Gestão de Programas
Acesse o menu **Admin > Programas**.
- **Visualização**: Lista completa de programas de Pós-Graduação (Mestrado/Doutorado).
- **Tipos de Oferta**: Identificação clara de cursos **Acadêmicos** e **Profissionais**.
- **Graduação**: Cursos de graduação são listados em uma seção separada ao final da página.
- **Resumo**: Card com estatísticas de totalizadores por nível e tipo.

### 3.1 Gestão de Editais
*   **Cadastro:** Registre novos editais com Número, Descrição e Agência de Fomento.
*   **Modalidades:** Dentro de cada edital, configure as bolsas (Nível, Valor, Vagas). Ex: Mestrado (R$ 2.100).

### 3.2 Gestão de Bolsistas
*   **Cadastro Individual:** Insira Nome, CPF, Dados Bancários e Vínculo (Edital/Modalidade/Programa).
*   **Importação em Massa (Novidade V5):**
    *   Vá em *Bolsistas > Importar (CSV)*.
    *   Carregue a planilha da CAPES.
    *   O sistema detecta automaticamente o vínculo e cria os registros.
*   **Filtros e Busca:**
    *   Clique nos cabeçalhos da tabela ("Status") para alternar entre Ativos, Inativos e Finalizando.
    *   Use a barra de busca para encontrar por Nome, CPF, SEI ou **Número do Formulário**.

### 3.3 Relatórios
*   **Folha de Pagamento:** Gere PDFs ou Excel para envio ao financeiro.
*   **Painel:** Visualize gráficos de distribuição de bolsas por nível e gastos mensais.

### 3.4 Geração de Certificados
*   Clique no botão **"📜 Gerar Certificados"** na tela de Bolsistas.
*   Busque o discente pelo nome.
*   O sistema gera o texto oficial (Bolsista ou Pós-Doc) automaticamente.
*   Copie e cole em seu editor de texto preferido.

---

## 4. Arquitetura do Sistema

O sistema foi construído sobre uma arquitetura **MVC Modular** utilizando **Flask** (Python).

### Estrutura de Pastas
*   `/app.py`: Controlador principal (Rotas e Regras de Negócio).
*   `/models.py`: Modelagem do Banco de Dados.
*   `/templates/`: Telas do sistema (HTML + Jinja2).
*   `/static/`: Estilos (CSS) e Imagens.
*   `/backups/`: Rotinas e arquivos de segurança.
*   `/docs/`: Documentação técnica.

---

## 5. Estrutura do Banco de Dados (Schema V5)

O banco de dados **SQLite** foi normalizado na Versão 5 para garantir integridade.

### Entidades Principais
1.  **Campus:** Tabela de domínio (13 campi da UTFPR).
2.  **ProgramaAcademico:** Vinculado ao Campus (1:N). Contém Nome e sigla do programa (PPG).
3.  **Edital:** Documento regulador.
4.  **Modalidade:** Regras financeiras do edital.
5.  **Bolsista:** Tabela Fato.
    *   *Chaves Estrangeiras:* `edital_id`, `modalidade_id`, `programa_id`.
    *   *Campos Críticos:* CPF (Único), Datas de Vigência, Status (Ativo/Inativo).

---

## 6. Histórico de Evolução

*   **V1-V2 (Protótipo):** Cadastro simples via planilhas soltas.
*   **V3 (Web):** Migração para Flask e SQLite. Interface básica.
*   **V4 (Estabilização):** Melhorias em relatórios e correção de bugs.
*   **V5 (Atual):**
    *   Normalização de Campus/Programas.
    *   Importação Inteligente CAPES DS.
    *   Segurança via `.env`.
    *   Novo Design com Tema Escuro/UTFPR.
*   **V6 (Atual - Dez/2025):**
    *   **Filtros de Status:** Visualização rápida de Bolsistas Ativos/Inativos/Finalizando com contadores dinâmicos.
    *   **Controle de Formulários:** Novo campo "Número do Formulário" para rastreio de propostas físicas.
    *   **Busca Avançada:** Pesquisa por número SEI, formulário e sigla de programa.
    *   **Dashboard Detalhado:** Inclusão de indicadores específicos para Pós-Doutorado (Resumo Geral).
*   **V6.2 (Atual - Jan/2026):**
    *   **Certificados:** Geração automática de declarações de vigência.
    *   **Pós-Doc:** Campos específicos (Projeto, Fomento) e lógica de visibilidade condicional.

---
*Este documento deve ser atualizado sempre que houver mudanças estruturais no banco de dados ou novas funcionalidades.*
