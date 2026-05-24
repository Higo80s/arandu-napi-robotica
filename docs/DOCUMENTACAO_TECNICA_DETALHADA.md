
# Manual Técnico de Arquitetura e Decisões de Projeto
**Sistema de Gestão de Editais - Versão 6.2**

---

## 1. Arquitetura de Banco de Dados e ORM

### 1.1 A Relação entre os Componentes
Para garantir flexibilidade e manutenibilidade, o sistema utiliza uma camada de abstração de dados. É importante distinguir os papéis de cada tecnologia:

*   **SQLite e PostgreSQL (Bancos de Dados):** São os sistemas gerenciadores de banco de dados (SGBD) onde as informações são efetivamente armazenadas.
*   **SQLAlchemy (ORM):** É o *Object Relational Mapper* (Mapeador Objeto-Relacional). Ele atua como um "tradutor universal".
    *   **Funcionamento:** No código Python (`models.py`), definimos Classes (ex: `class Bolsista`). O SQLAlchemy traduz essas classes e suas interações para comandos SQL (`CREATE TABLE`, `SELECT`, `INSERT`), independentemente do banco de dados utilizado.
    *   **Por que usar ORM?** Além de acelerar o desenvolvimento (evitando SQL manual repetitivo), ele protege contra injeção de SQL (SQL Injection) e permite trocar o banco de dados sem reescrever o código da aplicação.

### 1.2 Suporte a Banco de Dados Dual (Dual-Database Support)
O sistema foi projetado para operar em dois ambientes distintos com o mesmo código base. Esta lógica está implementada em `app.py`:

*   **Ambiente de Desenvolvimento (Local):** Utiliza **SQLite**.
    *   *Característica:* Um arquivo simples (`instance/gestao_editais_new.db`) que não requer instalação de servidor. Ideal para testes rápidos no computador do desenvolvedor.
*   **Ambiente de Produção (Servidor/Docker):** Utiliza **PostgreSQL**.
    *   *Característica:* Um SGBD robusto, cliente-servidor, otimizado para concorrência.
    *   *Detecção Automática:* O sistema verifica a variável de ambiente `DATABASE_URL`. Se ela existir, conecta-se ao Postgres; caso contrário, cria o arquivo SQLite.

---

## 2. Framework Web: Flask

### 2.1 A Escolha do Flask
Optou-se pelo micro-framework **Flask** em detrimento de opções mais pesadas como Django.

*   **Customização "Sob Medida":** O projeto possui regras de negócio muito específicas (cálculos de vigência baseados em editais, geração de relatórios PDF com layout da instituição). O Flask permite construir essas funcionalidades componente por componente, sem o "peso" de módulos desnecessários que vêm pré-instalados em frameworks maiores.
*   **Flexibilidade:** Permite integrar facilmente bibliotecas específicas para necessidades do projeto, como `xhtml2pdf` para relatórios e `SQLAlchemy` para dados.

### 2.2 Arquitetura MVC (Model-View-Controller)
Embora o Flask não imponha uma estrutura rígida, o projeto segue o padrão MVC para organização:
*   **Model (`models.py`):** Define a estrutura dos dados (Tabelas e Regras).
*   **View (`templates/`):** A interface com o usuário (HTML/CSS).
*   **Controller (`app.py`):** A lógica que recebe os pedidos do usuário, consulta o Model e devolve a View apropriada.

---

## 3. Normalização de Dados (3FN)

A **Terceira Forma Normal (3FN)** é um padrão de design de banco de dados aplicado para reduzir redundância e garantir a integridade dos dados.

### 3.1 Aplicação no Projeto
Anteriormente, campos como "Curso" e "Campus" eram textos livres. Isso gerava variações como "Eng. Mecânica", "Engenharia Mecânica" e "Mecânica", que o sistema tratava como cursos diferentes.

**Na versão atual (V5+):**
*   Foram criadas tabelas auxiliares: `Campus` e `ProgramaAcademico`.
*   Na tabela `Bolsistas`, não salvamos mais o *nome* do curso, mas sim o seu **ID** (Chave Estrangeira).
*   **Benefício:** Se o nome do curso precisar ser corrigido, altera-se apenas no registro do Curso, e a correção se reflete para todos os bolsistas vinculados instantaneamente.

---

## 4. Infraestrutura e Deployment

### 4.1 Containerização (Docker)
O uso do Docker cria um ambiente isolado e reprodutível.
*   **Problema Resolvido:** Elimina a falha "na minha máquina funciona". O Dockerfile define exatamente qual versão do Linux e do Python o sistema precisa.
*   **Independência:** O sistema roda da mesma maneira no notebook do desenvolvedor e no servidor da universidade, independente do que esteja instalado no sistema operacional hospedeiro.

### 4.2 Servidor de Aplicação (WSGI e Gunicorn)
*   **WSGI (Web Server Gateway Interface):** É o protocolo padrão de comunicação entre servidores web e aplicações Python.
*   **Gunicorn:** É o servidor HTTP que implementa o WSGI com robustez.
    *   *O Fluxo:* A internet (Nginx/Apache) fala com o **Gunicorn**, que gerencia múltiplos processos ("workers") para atender várias requisições simultâneas, e então repassa para o **Flask** processar a lógica.
    *   *Por que:* O servidor embutido do Flask é monothread e frágil, adequado apenas para testes. O Gunicorn é necessário para suportar tráfego real em produção.

---

## 5. Segurança e Compliance

### 5.1 Registro no INPI (Propriedade Intelectual)
Para o registro de software, é necessário garantir a integridade e autoria do código.
*   **Hash SHA-256:** Foi implementado um script (`scripts/prepare_inpi_files.py`) que percorre todos os arquivos fonte essenciais do projeto e gera um código HASH único (assinatura digital). Qualquer alteração de uma única vírgula no código muda completamente esse Hash, garantindo ao INPI a versão exata que foi registrada.

### 5.2 Segurança de Dados
*   **Prevenção a SQL Injection:** O uso do SQLAlchemy sanitiza todas as entradas de dados antes de enviar ao banco.
*   **Segurança de Sessão:** Uso de `SECRET_KEY` rotativa e variáveis de ambiente (`.env`) para que senhas nunca fiquem salvas no código fonte.
*   **Logs de Auditoria Básicos:** O sistema registra erros críticos e transações de banco de dados, permitindo rastreabilidade técnica.

---

**Equipe de Desenvolvimento de TI**
*Documento gerado automaticamente para fins de auditoria e transferência tecnológica.*
