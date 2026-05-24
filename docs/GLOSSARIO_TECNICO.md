# Dicionário Técnico Extensivo: Gestão de Editais
**Referência Completa de Termos, Acrônimos e Conceitos do Projeto**

Este documento compila uma vasta lista de termos técnicos utilizados no desenvolvimento, infraestrutura e negócio do sistema. Use como "Enciclopédia" para consulta rápida.

---

## 0-9
*   **3FN (Terceira Forma Normal)**: Regra de normalização de banco de dados aplicada na versão V5 do projeto para eliminar redundâncias (ex: separar Campus e Programas em tabelas próprias).
*   **404 Not Found**: Código de status HTTP que indica que a rota ou recurso solicitado não existe.
*   **500 Internal Server Error**: Código HTTP indicando erro no servidor (Python/Flask), geralmente capturado pelos logs do Gunicorn.

## A
*   **ABC (Abstract Base Class)**: Conceito Python (módulo `abc`) para definir classes abstratas, garantindo que subclasses implementem métodos específicos.
*   **ACID**: Propriedades de transações de banco (Atomicidade, Consistência, Isolamento, Durabilidade), garantidas pelo PostgreSQL.
*   **Action (HTML Form)**: Atributo da tag `<form>` que define para qual URL os dados serão enviados (ex: `action="/bolsistas/novo"`).
*   **Adapter Pattern**: Padrão de projeto utilizado quando adaptamos o driver de banco de dados (SQLite -> Postgres -> Oracle).
*   **Agile**: Metodologia de desenvolvimento ágil que seguimos (entregas incrementais, feedback constante).
*   **Alembic**: Ferramenta de migração de banco de dados para SQLAlchemy (gerencia `versions/` do schema).
*   **Algorithm**: Lógica sequencial para resolver problemas. Ex: O algoritmo de cálculo de vigência em `app.py`.
*   **Alias (SQL)**: Apelido dado a uma tabela numa query (ex: `SELECT * FROM bolsistas AS b`).
*   **Alpine Linux**: Distribuição Linux ultra-leve, frequentemente usada como base para imagens Docker (`python:3.11-alpine`), embora usemos `slim` (Debian) para compatibilidade.
*   **API (Application Programming Interface)**: Interface que permite comunicação entre sistemas. Nosso Dashboard consome uma API interna JSON.
*   **App Context (Flask)**: Contexto de aplicação que permite acesso a variáveis globais como `current_app` e `g`.
*   **Append**: Método Python para adicionar itens ao final de uma lista (`lista.append(item)`).
*   **Argument (Arg)**: Valor passado para uma função ou script (ex: `python app.py --port=5000`).
*   **Array**: Estrutura de dados (Lista em Python). No JavaScript, manipulamos arrays de opções de dropdown.
*   **Assert**: Declaração usada em testes (`scripts/test_ramones.py`) para verificar se uma condição é verdadeira.
*   **Async/Await**: Sintaxe para programação assíncrona. O Flask suporta (via `async` routes), mas usamos o modelo síncrono padrão (WSGI) pela simplicidade.
*   **AttributeError**: Erro Python comum quando tentamos acessar um atributo inexistente em um objeto (ex: `None.campus`).
*   **Audit Log**: Registro de atividades (quem fez o que). Implementado parcialmente nos logs do Gunicorn e tabelas de histórico.
*   **Authentication (Auth)**: Processo de verificar identidade (Login).
*   **Authorization**: Processo de verificar permissão (O que o usuário logado pode fazer).
*   **Auto-Increment**: Coluna de banco que gera IDs sequenciais automaticamente (1, 2, 3...).
*   **Auto-Reload**: Funcionalidade do Flask em modo Debug que reinicia o servidor ao salvar arquivos.

## B
*   **Backend**: A "parte de trás" do sistema (Python/Flask/DB). Onde a lógica acontece.
*   **Background Task**: Tarefa que roda em segundo plano.
*   **Backup**: Cópia de segurança dos dados. No Postgres, feito via `pg_dump`.
*   **Base64**: Método de codificação de dados binários em texto. Usado às vezes para embutir imagens pequenas no CSS/HTML.
*   **Bash**: Shell padrão do Linux. Usado nos scripts de `entrypoint` do Docker.
*   **Batch Processing**: Processamento em lote. Ex: Importação de CSV de bolsistas processa centenas de linhas de uma vez.
*   **Bin (Binary)**: Executável ou arquivo compilado.
*   **Bind (Docker)**: Tipo de montagem de volume que liga uma pasta do Host ao Container.
*   **Bind (Gunicorn)**: Endereço IP e Porta onde o servidor escuta (ex: `0.0.0.0:5000`).
*   **Blob (Binary Large Object)**: Tipo de dado para armazenar arquivos no banco (evitamos, preferimos File System).
*   **Blocking**: Operação que trava a execução até terminar.
*   **Blueprint (Flask)**: Forma de organizar a aplicação em módulos (ex: `/auth`, `/admin`, `/posdoc`). Essencial para projetos grandes.
*   **Body (HTTP)**: Corpo da requisição onde vão os dados do formulário (POST).
*   **Boilerplate**: Código padrão repetitivo necessário para iniciar um projeto.
*   **Boolean**: Tipo de dado Verdadeiro/Falso (`True`/`False`). Usado em `bolsista.ativo`.
*   **Bootstrap**: Framework CSS usado para o layout responsivo e componentes visuais (Cards, Navbars).
*   **Branch (Git)**: Ramificação do código para desenvolver features isoladas (`main`, `develop`, `feature/zootecnia`).
*   **Breakpoint**: Ponto de parada na execução para Debugging.
*   **Browser**: Navegador web (Chrome, Firefox). O cliente da nossa aplicação.
*   **Build (Docker)**: Processo de criar uma imagem Docker a partir do `Dockerfile`.
*   **Bytecode**: Código intermediário (`.pyc`) gerado pelo Python.
*   **Bytes**: Unidade de informação digital.

## C
*   **Cache**: Armazenamento temporário para acesso rápido. O navegador faz cache de CSS/JS.
*   **Callback**: Função passada como argumento para ser executada depois. Comum em JavaScript.
*   **CamelCase**: Estilo de nomeação (`NomeDaVariavel`). Em Python usamos `snake_case` (`nome_da_variavel`).
*   **Canvas (HTML5)**: Elemento para desenho gráfico dinâmico. Usado pela biblioteca Chart.js no nosso Dashboard.
*   **Cascade Delete**: Regra de banco. Se apagar um Edital, apaga os bolsistas vinculados automaticamente (Configurado no SQLAlchemy).
*   **Case Sensitive**: Diferencia maiúsculas de minúsculas (Python é, SQL depende do banco).
*   **Catch (Try/Except)**: Captura de erros. Em Python é `except`.
*   **CharField**: Campo de texto curto.
*   **Chart.js**: Biblioteca JS usada para os gráficos do Dashboard.
*   **Check constraint**: Regra validação no banco (ex: `valor > 0`).
*   **Class (OOP)**: Modelo para criar objetos. Ex: `class Bolsista(db.Model):`.
*   **Clean Code**: Filosofia de escrever código legível e manutenível (ex: nomes de variáveis claros).
*   **Client-Side**: Tudo que roda no navegador do usuário (JS, CSS).
*   **Clone (Git)**: Copiar um repositório remoto para a máquina local.
*   **Cloud**: Computação em nuvem (AWS, Azure, PythonAnywhere).
*   **Column (SQLAlchemy)**: Define uma coluna na tabela (`db.Column`).
*   **Command Line Interface (CLI)**: Interface de Linha de Comando (Terminal, PowerShell).
*   **Commit (Git)**: Salvar mudanças no histórico de versão.
*   **Commit (SQL)**: Confirmar transação no banco de dados. Sem isso, os dados não persistem.
*   **Compiler**: Tradutor de código fonte para código máquina. Python é interpretado, mas compila para bytecode.
*   **Component**: Parte isolada da interface.
*   **Composer**: Gerenciador de dependências PHP (não usamos, mas bom saber o análogo ao `pip`).
*   **Concurrency**: Capacidade de lidar com múltiplas tarefas "ao mesmo tempo". O Gunicorn habilita isso via Workers.
*   **Config Vars**: Variáveis de configuração (`FLASK_ENV`, `DATABASE_URL`).
*   **Conflict (Git)**: Quando duas pessoas editam a mesma linha de código.
*   **Connection String**: URL contendo usuário, senha e host para conectar ao banco.
*   **Console**: Janela de texto para interagir com o sistema ou ver logs (F12 no navegador).
*   **Constant**: Valor que não muda (ex: `PI = 3.14`). Em Python, usamos UPPERCASE por convenção.
*   **Constructor**: Método `__init__` em Python.
*   **Container**: Unidade de software isolada (Docker) contendo código e dependências.
*   **Context Manager**: Estrutura `with ...` em Python (ex: `with app.app_context():`). Garante fechamento de recursos.
*   **Cookie**: Pequeno arquivo de texto salvo no navegador para lembrar do usuário.
*   **CORS (Cross-Origin Resource Sharing)**: Política de segurança do navegador que bloqueia requisições entre domínios diferentes.
*   **CPU Bound**: Tarefa limitada pela velocidade do processador.
*   **Cron Job**: Tarefa agendada no Linux/Unix (ex: Rodar backup todo dia às 3am).
*   **CRUD**: Create, Read, Update, Delete. As 4 operações básicas de qualquer sistema de cadastro.
*   **CSS (Cascading Style Sheets)**: Estilos visuais.
*   **CSV (Comma Separated Values)**: Formato de arquivo simples para troca de dados (Excel interopera bem).
*   **Cursor (Database)**: Objeto que permite percorrer os resultados de uma query.

## D
*   **Daemon**: Processo que roda em segundo plano (background) no sistema operacional. O Docker Engine é um daemon.
*   **Dashboard**: Painel de controle visual com métricas e indicadores.
*   **Data Science**: Ciência de dados. Python é a linguagem líder nesta área.
*   **Data Structure**: Forma de organizar dados (Lista, Dicionário, Tupla, Set).
*   **Data Type**: Tipo do dado (Integer, String, Float, Boolean, Date).
*   **Database (DB)**: Sistema organizado para armazenar, gerenciar e recuperar informações.
*   **DataFrame**: Estrutura tabular da biblioteca **Pandas** (usada na análise de dados e exportação Excel).
*   **Dateutil**: Biblioteca Python poderosa para cálculos de data (`relativedelta`).
*   **Dead Code**: Código que nunca é executado e deve ser removido.
*   **Debug**: Processo de encontrar e corrigir defeitos (bugs).
*   **Decimal**: Tipo de dado para dinheiro (evita erros de arredondamento de Float).
*   **Decorator**: Função que modifica outra função (ex: `@app.route('/')`). Padrão muito usado no Flask.
*   **Deep Copy**: Cópia completa de um objeto e seus filhos.
*   **Default**: Valor padrão.
*   **Dependency Injection**: Padrão de projeto para injetar dependências em vez de criá-las internamente.
*   **Dependency**: Biblioteca externa que o projeto precisa (`requirements.txt`).
*   **Deploy**: Implantação. Colocar o sistema no ar.
*   **Deprecated**: Recurso obsoleto que será removido no futuro.
*   **Design Pattern**: Solução recorrente para problemas comuns (Singleton, Factory, MVC).
*   **DevOps**: Cultura/Práticas de união entre Desenvolvimento e Operações (Deploy, CI/CD).
*   **Dict (Dictionary)**: Estrutura de dados chave-valor em Python (`{'chave': 'valor'}`). Análogo ao JSON Object.
*   **Diff**: Diferença entre dois arquivos ou versões.
*   **Directory**: Pasta.
*   **Django**: Outro framework web Python, mais "pesado" que o Flask.
*   **DNS (Domain Name System)**: Traduz nomes (www.google.com) para IPs.
*   **Docstring**: String de documentação no início de funções/classes (`""" Explica o que faz """`).
*   **Docker**: Plataforma de containerização.
*   **Docker Compose**: Orquestrador de containers locais.
*   **Docker Hub**: Repositório público de imagens Docker.
*   **Dockerfile**: Receita para construir uma imagem Docker.
*   **DOM (Document Object Model)**: Estrutura em árvore que representa o HTML na memória do navegador. O JavaScript manipula o DOM.
*   **Domain**: Área de conhecimento do problema (ex: Domínio Acadêmico) ou endereço web.
*   **Dotenv (.env)**: Arquivo para guardar variáveis de ambiente locais.
*   **Download**: Baixar dados do servidor.
*   **Driver**: Software que permite o sistema falar com o Hardware ou Banco de Dados (ex: `psycopg2` para Postgres).
*   **Drop Table**: Comando SQL destrutivo que apaga uma tabela inteira.
*   **DRY (Don't Repeat Yourself)**: Princípio de não repetir código.
*   **Dump**: Exportação completa de dados (banco ou memória).
*   **Dynamic Typing**: Tipagem dinâmica (Python), onde não precisa declarar o tipo da variável (`x = 10` e depois `x = "oi"`).

## E
*   **Easter Egg**: Recurso escondido no software (não temos, somos profissionais!).
*   **Ecosystem**: Conjunto de ferramentas e bibliotecas de uma linguagem (Ecossistema Python).
*   **Editor**: Software para escrever código (VS Code, Sublime, Notepad++).
*   **Elevator Pitch**: Discurso de elevador (pitch de vendas rápido).
*   **Encapsulation**: Pilar da OO. Esconder detalhes internos do objeto.
*   **Endpoint**: URL de uma API (ex: `/api/dados-financeiros`).
*   **Entity (ER Model)**: Entidade do banco de dados (Tabela).
*   **Entrypoint**: Script ou comando executado ao iniciar um container Docker.
*   **Enum (Enumeration)**: Tipo de dado para lista fixa de valores (ex: Status: ATIVO, INATIVO).
*   **Environment (Env)**: Ambiente (Dev, Test, Prod).
*   **Environment Variable**: Variável do sistema operacional acessível pelo código.
*   **Error Handling**: Tratamento de erros (`try/except`).
*   **ETL (Extract, Transform, Load)**: Processo de mover dados de um lugar para outro. Usado na nossa importação de CSV.
*   **Event Listener**: (JS) Função que "escuta" um evento (clique, digitação) para reagir.
*   **Exception**: Erro que ocorre durante a execução (Runtime Error).
*   **Execute (SQL)**: Rodar um comando SQL.
*   **Exit Code**: Código retornado por um processo ao terminar (0 = Sucesso, 1+ = Erro).
*   **Export**: Salvar dados para fora (Gerar PDF, Excel).
*   **Extension (Flask)**: Plugin para o Flask (ex: `Flask-SQLAlchemy`, `Flask-Migrate`).

## F
*   **Factory Pattern**: Padrão de criar objetos via função (`create_app()`). Usamos Application Factory no Flask.
*   **Failover**: Capacidade de mudar para um sistema redundante se o principal falhar.
*   **Favicon**: Ícone do site na aba do navegador.
*   **Feature**: Funcionalidade nova.
*   **Fetch API**: API moderna do JavaScript para fazer requisições HTTP (substitui AJAX/XMLHttpRequest).
*   **Field**: Campo de um formulário ou coluna de tabela.
*   **File System**: Sistema de arquivos do SO.
*   **Filter (Jinja2)**: Função para formatar dados no template (ex: `{{ valor | currency }}`).
*   **Firewall**: Sistema de segurança que filtra tráfego de rede.
*   **Flag**: Variável booleana para sinalizar estado (ex: `has_error = True`).
*   **Flask**: Microframework web Python.
*   **Float**: Número com ponto flutuante (decimal).
*   **For Loop**: Estrutura de repetição.
*   **Foreign Key (FK)**: Chave Estrangeira. Campo que liga uma tabela a outra (ex: `programa_id` em `bolsistas` aponta para `id` em `programa_academico`).
*   **Fork**: Cópia de um projeto para desenvolvimento independente.
*   **Form Data**: Dados enviados por um formulário HTML.
*   **Format String (f-string)**: Recurso do Python 3.6+ (`f"Ola {nome}"`).
*   **Framework**: Estrutura de código que fornece base para desenvolvimento (Flask).
*   **Frontend**: A "frente" do sistema (HTML/CSS/JS). O que o usuário vê.
*   **Full Stack**: Desenvolvedor que atua no Frontend e Backend.
*   **Function**: Bloco de código reutilizável.

## G
*   **Garbage Collection**: Gerenciamento automático de memória do Python.
*   **GET (HTTP)**: Método para PEDIR dados ao servidor.
*   **Git**: Sistema de controle de versão distribuído.
*   **GitHub**: Plataforma de hospedagem de código Git.
*   **Global Variable**: Variável acessível em todo o código (evitamos, má prática).
*   **Globbing**: Uso de coringas em caminhos de arquivo (`*.py`).
*   **Glossary**: Este documento!
*   **GUI (Graphical User Interface)**: Interface Gráfica (Janelas, botões). Nosso sistema é Web GUI.
*   **Gunicorn (Green Unicorn)**: Servidor HTTP WSGI para UNIX. Roda nossa app em produção.

## H
*   **Hardcoded**: Valor fixo escrito diretamente no código (Má prática para senhas/config).
*   **Hash Map**: Estrutura de dados (Dicionário).
*   **Hashing**: Criptografia de via única (SHA-256).
*   **Head (HTML)**: Cabeçalho do arquivo HTML (metadados, links CSS).
*   **Head (HTTP)**: Método que pede apenas cabeçalhos, sem corpo.
*   **Header (HTTP)**: Informações meta da requisição (User-Agent, Content-Type).
*   **Hello World**: Primeiro programa que se faz ao aprender uma linguagem.
*   **Helper**: Função auxiliar para tarefas repetitivas.
*   **Hex (Hexadecimal)**: Sistema numérico base 16. Usado em cores CSS (`#FFFFFF`).
*   **Host**: O computador servidor.
*   **HTML (HyperText Markup Language)**: Linguagem de marcação web.
*   **HTTP (HyperText Transfer Protocol)**: Protocolo da Web.
*   **HTTPS**: Versão segura (Criptografada) do HTTP.
*   **Hyperlink**: Link clicável.

## I
*   **IDE**: Ambiente de Desenvolvimento Integrado.
*   **Idempotency**: Propriedade de uma operação que pode ser repetida várias vezes sem mudar o resultado além da primeira vez.
*   **Identity Column**: Coluna de auto-incremento no Oracle/Postgres modernos.
*   **If/Else**: Estrutura condicional.
*   **Image**: Arquivo de imagem ou Imagem Docker.
*   **Immutable**: Objeto que não pode ser mudado após criado (ex: Tupla em Python).
*   **Import**: Comando para carregar módulos (`import os`).
*   **Indentação**: Espaçamento no início da linha. Em Python, define os blocos de código e é obrigatório.
*   **Index (Database)**: Estrutura que acelera as buscas no banco.
*   **Index (List)**: Posição de um item na lista (começa em 0).
*   **Inheritance**: Herança. Pilar da OO.
*   **Init Script**: Script de inicialização.
*   **Injection**: Injeção de dependência ou de código malicioso.
*   **Input**: Entrada de dados.
*   **Instance**: Objeto criado a partir de uma classe.
*   **Integer (Int)**: Número inteiro.
*   **Integration Test**: Teste que verifica se diferentes partes do sistema funcionam juntas.
*   **Interface**: Contrato que define métodos que uma classe deve ter.
*   **Interpreter**: Programa que executa scripts Python (`python.exe`).
*   **IO Bound**: Tarefa limitada pela velocidade de entrada/saída (Disco/Rede).
*   **IP Address**: Endereço numérico na rede.
*   **Iterable**: Objeto que pode ser percorrido num loop.
*   **Iterator**: Objeto que percorre um iterável.

## J
*   **Java**: Linguagem popular (concorrente/alternativa ao Python no backend).
*   **JavaScript (JS)**: Linguagem de script do navegador.
*   **Jinja2**: Motor de templates do Flask.
*   **Join (SQL)**: Comando para combinar linhas de duas ou mais tabelas.
*   **JSON (JavaScript Object Notation)**: Formato leve de troca de dados.
*   **JWT (JSON Web Token)**: Padrão para autenticação via token (alternativa a sessões).

## K
*   **Kernel**: Núcleo do sistema operacional.
*   **Key-Value Pair**: Par Chave-Valor.
*   **Keyword**: Palavra reservada da linguagem (`def`, `class`, `if`).
*   **Kill**: Comando para terminar um processo forçadamente.

## L
*   **Lambda**: Função anônima em Python (`lambda x: x*2`).
*   **Latency**: Tempo de atraso na rede.
*   **Lazy Loading**: Carregamento preguiçoso. O SQLAlchemy não busca dados relacionados até você pedir (`lazy=True`).
*   **Legacy Code**: Código legado. Código antigo que ainda está em uso.
*   **Lib (Library)**: Biblioteca de código.
*   **License**: Permissão de uso de software.
*   **Lint/Linter**: Ferramenta que analisa código estático buscando erros de estilo (nossos avisos de erro em JS).
*   **List Comprehension**: Sintaxe elegante para criar listas em Python (`[x for x in lista]`).
*   **Load Balancer**: Distribuidor de carga.
*   **Localhost**: O computador local (`127.0.0.1`).
*   **Log**: Registro de eventos.
*   **Logic Error**: Erro onde o código roda, mas faz a coisa errada (bug).
*   **Login**: Processo de entrar no sistema.
*   **Logout**: Sair do sistema.
*   **Loop**: Repetição.

## M
*   **Macro (Jinja2)**: Função reutilizável dentro de templates HTML.
*   **Main**: Função principal do programa.
*   **Manifest**: Arquivo que descreve pacote ou deploy.
*   **Map**: Função que aplica uma transformação a cada item de uma lista.
*   **Markdown (.md)**: Linguagem de marcação leve usada nesta documentação.
*   **Master/Main Branch**: Ramificação principal do Git.
*   **Memory Leak**: Vazamento de memória. Quando o programa consome RAM e não devolve.
*   **Merge**: Unir branches no Git ou dados no Banco.
*   **Metadata**: Dados sobre dados.
*   **Method**: Função dentro de uma classe.
*   **Microservices**: Arquitetura de dividir o sistema em serviços pequenos (oposto de Monólito). Nosso sistema é Monólito Modular.
*   **Middleware**: Software que fica entre o SO e a Aplicação, ou entre o Request e o Controller.
*   **Migration**: Alteração controlada no esquema do banco de dados.
*   **Mock**: Objeto falso usado em testes para simular comportamento.
*   **Modal**: Janela flutuante na interface web.
*   **Model**: Representação dos dados código.
*   **Module**: Arquivo Python (`.py`) importável.
*   **Monolith**: Aplicação onde todo código está em um único projeto (nosso caso, que é bom para começar).
*   **Mount (Docker)**: Montar um volume ou diretório.
*   **MVC**: Model-View-Controller.
*   **MVP**: Minimum Viable Product.
*   **MySQL**: Outro banco de dados popular.

## N
*   **Namespace**: Espaço de nomes para evitar conflitos.
*   **Native**: Recurso original da plataforma.
*   **Navbar**: Barra de navegação.
*   **Nginx**: Servidor Web de alta performance usado como Proxy Reverso à frente do Gunicorn.
*   **Node.js**: Runtime JS fora do navegador. Usamos Python, mas Node é comum no frontend moderno.
*   **None**: O "nulo" do Python.
*   **NoSQL**: Banco não-relacional (ex: MongoDB). Não usamos.
*   **Null**: Valor nulo em SQL.
*   **NumPy**: Biblioteca Python para computação numérica (base do Pandas).

## O
*   **Object**: Instância de uma classe.
*   **Object-Oriented Programming (OOP)**: Programação Orientada a Objetos. Paradigma que usamos em Python.
*   **Offset**: Deslocamento (usado em paginação SQL).
*   **One-to-Many**: Relacionamento 1 para N (1 Edital tem N Bolsistas).
*   **One-to-One**: Relacionamento 1 para 1.
*   **Open Source**: Código aberto.
*   **Operator**: Símbolos de operação (+, -, ==).
*   **Optimization**: Melhorar performance.
*   **Oracle DB**: Banco de dados Enterprise da Oracle.
*   **Oracle Thin Client**: Driver leve para conectar no Oracle.
*   **ORM**: Object-Relational Mapping.
*   **OS (Operating System)**: Sistema Operacional.
*   **Output**: Saída de dados.
*   **Overhead**: Custo extra de processamento.
*   **Override**: Sobrescrever um método herdado.

## P
*   **Packet**: Pacote de rede.
*   **Pagination**: Dividir resultados em páginas.
*   **Pandas**: Biblioteca Python para análise de dados (Excel/CSV).
*   **Parameter**: Variável na definição da função.
*   **Parse**: Analisar e interpretar dados (ex: Parsear CSV).
*   **Pass**: Comando Python que não faz nada (placeholder).
*   **Password**: Senha.
*   **Patch**: Correção de bug.
*   **Path**: Caminho de arquivo.
*   **Payload**: Carga útil de dados numa requisição.
*   **PDF (Portable Document Format)**: Formato de documento gerado pelo sistema.
*   **PEP-8**: Guia de estilo oficial do Python.
*   **Performance**: Desempenho.
*   **Persistence**: Gravar dados para que não se perdam (Banco de Dados).
*   **PIP**: Gerenciador de pacotes do Python (`pip install`).
*   **Pipeline**: Sequência de processos.
*   **Pivot Table**: Tabela dinâmica.
*   **Pixel**: Ponto na tela.
*   **Placeholder**: Texto temporário ou de exemplo.
*   **Platform**: Hardware/Software onde o sistema roda.
*   **Plugin**: Extensão.
*   **Polyfill**: Código para dar suporte a recursos novos em navegadores velhos.
*   **Polymorphism**: Pilar da OO. Tratar objetos diferentes de forma igual.
*   **Port**: Porta de rede (5000 para Flask, 5432 para Postgres).
*   **POST (HTTP)**: Método para ENVIAR dados (criar/salvar).
*   **PostgreSQL**: Nosso Banco de Dados de produção.
*   **Primary Key (PK)**: Identificador único de uma linha na tabela (ID).
*   **Print**: Função para exibir texto no console.
*   **Private**: Métodos/Atributos internos (`_variavel`).
*   **Process**: Programa em execução.
*   **Production (Prod)**: Ambiente real de uso.
*   **Promise (JS)**: Objeto para lidar com assincronismo em JS.
*   **Prompt**: Solicitação de comando.
*   **Property**: Decorator Python (`@property`) para criar getters.
*   **Protocol**: Regras de comunicação (HTTP, TCP, IP).
*   **Prototype**: Protótipo.
*   **Proxy**: Servidor intermediário.
*   **Pull Request (PR)**: Pedido para mesclar código no Git.
*   **Push**: Enviar código para o Git remoto.
*   **PUT (HTTP)**: Método para ATUALIZAR dados inteiros.
*   **PyPI**: Repositório oficial de pacotes Python.
*   **Pythonic**: Jeito idiomático e elegante de escrever Python.

## Q
*   **QA (Quality Assurance)**: Garantia de qualidade (Testes).
*   **Query**: Consulta ao banco de dados.
*   **Query String**: Parâmetros na URL (`?busca=teste`).
*   **Queue**: Fila.

## R
*   **Race Condition**: Erro quando dois processos tentam mudar o mesmo dado ao mesmo tempo.
*   **RAM**: Memória de acesso aleatório.
*   **Range**: Função Python que gera sequência de números.
*   **React**: Framework JS (Não usamos, usamos Vanilla/HTML server-side).
*   **Read-Only**: Somente leitura.
*   **Readme**: Arquivo de leia-me inicial.
*   **Recursion**: Função que chama a si mesma.
*   **Refactor**: Reescrever código para melhorar a estrutura sem mudar o comportamento.
*   **Regression**: Bug que volta a aparecer depois de corrigido ou quebra de algo que funcionava.
*   **Relational Database**: Banco de dados baseado em tabelas relacionadas.
*   **Relationship**: Vínculo entre tabelas.
*   **Release**: Lançamento de versão.
*   **Reload**: Recarregar.
*   **Remote**: Repositório Git no servidor (GitHub).
*   **Render**: Gerar o HTML final a partir de um template.
*   **Repository (Repo)**: Local onde o código versionado fica.
*   **Request**: Requisição HTTP.
*   **Requirement**: Requisito do sistema ou dependência (`requirements.txt`).
*   **Response**: Resposta HTTP.
*   **Responsive**: Site que se adapta a telas pequenas (Mobile).
*   **REST (Representational State Transfer)**: Estilo de arquitetura para APIs.
*   **Return**: Devolver valor de uma função.
*   **Reverse Proxy**: Servidor (Nginx) que fica na frente da aplicação para segurança e load balancing.
*   **Rollback**: Desfazer transação no banco em caso de erro.
*   **Root**: Usuário administrador (Linux) ou diretório raiz `/`.
*   **Route**: Caminho da URL mapeado para uma função Python (`@app.route`).
*   **Row**: Linha de uma tabela.
*   **Runtime**: Tempo de execução ou ambiente de execução.

## S
*   **Sandbox**: Ambiente isolado para testes seguros.
*   **Sanitization**: Limpeza de dados de entrada para segurança.
*   **Scalability**: Capacidade de crescer.
*   **Schema**: Estrutura do banco de dados (Tabelas, Colunas).
*   **Scope**: Escopo de visibilidade de variáveis.
*   **Script**: Programa interpretado simples.
*   **Scrum**: Metodologia ágil.
*   **SDK (Software Development Kit)**: Kit de desenvolvimento.
*   **Search Engine**: Motor de busca.
*   **Secret Key**: Chave criptográfica usada pelo Flask.
*   **Security Toogle**: Funcionalidade de segurança.
*   **Seed**: Dados iniciais para popular o banco.
*   **Select**: Comando SQL para buscar dados.
*   **Self**: Referência à própria instância em métodos de classe Python.
*   **Semantic HTML**: Usar tags com significado (`<header>`, `<footer>`) em vez de apenas `<div>`.
*   **Server**: Computador ou software que serve recursos.
*   **Server-Side**: Lógica que roda no servidor (Python).
*   **Session**: Dados do usuário mantidos durante a navegação.
*   **Shell**: Interface de comando do SO.
*   **Sidebar**: Barra lateral do menu.
*   **Singleton**: Padrão onde só existe uma instância da classe.
*   **Site Reliability Engineering (SRE)**: Engenharia de confiabilidade (DevOps avançado).
*   **Slug**: Versão amigável de URL de um título.
*   **Snake Case**: Estilo `nome_da_variavel`.
*   **Snapshot**: Foto instantânea do estado do sistema.
*   **Socket**: Ponto final de comunicação de rede.
*   **Soft Delete**: "Deletar" marcando uma flag `ativo=False` em vez de apagar o registro. Usamos muito!
*   **Software**: Programa de computador.
*   **Sort**: Ordenar.
*   **Source Code**: Código fonte.
*   **SQL (Structured Query Language)**: Linguagem de banco de dados.
*   **SQLAlchemy**: Nosso ORM.
*   **SSL (Secure Sockets Layer)**: Tecnologia de criptografia para HTTPS.
*   **Stack Trace**: Rastreio da pilha de erros quando ocorre uma exceção.
*   **Stack**: Pilha de tecnologias (Python + Flask + Postgres).
*   **Staging**: Ambiente de pré-produção (Testes finais).
*   **Standard Library**: Biblioteca padrão que vem com o Python.
*   **State**: Estado atual da aplicação.
*   **Stateless**: Sem estado persistente na memória.
*   **Static Assets**: Arquivos estáticos (Imagens, CSS, JS).
*   **Status Code**: Código numérico da resposta HTTP (200, 404, 500).
*   **String**: Texto.
*   **Subquery**: Query dentro de outra Query.
*   **Superuser**: Administrador.
*   **Syntax Error**: Erro de escrita no código.
*   **Syntax**: Regras da linguagem.
*   **Sysadmin**: Administrador de sistemas.

## T
*   **Table**: Tabela de banco de dados.
*   **Tag (Git)**: Marcador de versão (v1.0).
*   **Tag (HTML)**: Elemento de marcação (`<div>`).
*   **TCP/IP**: Protocolo base da Internet.
*   **Template Engine**: Jinja2.
*   **Template**: Modelo HTML com lacunas para dados.
*   **Terminal**: Interface de texto.
*   **Test Case**: Caso de teste.
*   **Testing**: Testes.
*   **Text Editor**: Editor de texto.
*   **Thread**: Linha de execução leve dentro de um processo.
*   **Timezone**: Fuso horário.
*   **Token**: Chave de segurança temporária.
*   **Tool**: Ferramenta.
*   **Traceback**: Relatório de erro do Python.
*   **Transaction**: Conjunto de operações de banco atômicas.
*   **Trigger**: Gatilho de banco de dados acionado por evento (Insert/Update).
*   **Truncate**: Esvaziar tabela rápido.
*   **Try/Except**: Bloco de tratamento de erro.
*   **Tuple**: Lista imutável em Python.
*   **Type Hinting**: Anotações de tipo em Python (`def soma(a: int) -> int:`).
*   **Typography**: Estilo de fonte.

## U
*   **UI (User Interface)**: Interface do Usuário.
*   **Unicode**: Padrão de codificação de texto global (permite acentos, emojis).
*   **Unit Test**: Teste de unidade (testar uma função isolada).
*   **Unix**: Família de SOs (Linux, macOS).
*   **Update**: Atualizar dados.
*   **Upgrade**: Melhorar versão.
*   **Upload**: Enviar arquivo para o servidor.
*   **Uptime**: Tempo que o servidor está ligado sem cair.
*   **URI (Uniform Resource Identifier)**: Identificador de recurso (String de conexão do banco).
*   **URL (Uniform Resource Locator)**: Endereço web.
*   **User Experience (UX)**: Experiência do usuário.
*   **User**: Usuário.
*   **UTF-8**: Codificação de caracteres padrão da Web e Python 3.
*   **Utility**: Função utilitária.
*   **UUID (Universally Unique Identifier)**: Identificador único global.

## V
*   **Validation**: Verificação de dados (Frontend e Backend).
*   **Variable**: Espaço na memória para guardar valor.
*   **Venv (Virtual Environment)**: Ambiente virtual Python isolado.
*   **Version Control**: Controle de versão (Git).
*   **View (Database)**: Tabela virtual baseada em uma query.
*   **View (MVC)**: A camada de apresentação.
*   **Virtual Machine (VM)**: Máquina Virtual.
*   **Virtualization**: Criar versões virtuais de recursos.
*   **Volume (Docker)**: Persistência de dados.
*   **VPN**: Rede Privada Virtual.

## W
*   **W3C**: Consórcio que define padrões Web.
*   **Waitress**: Servidor WSGI puro Python para Windows/Linux (Usado no projeto para produção simples).
*   **Warning**: Aviso (não é erro, mas requer atenção).
*   **Waterfall**: Metodologia "Cascata" (oposto de Agile).
*   **Web Server**: Servidor Web (Nginx, Apache).
*   **Webhook**: CAllback via HTTP entre sistemas.
*   **Webpack**: Empacotador de JS (não usamos, mas é comum).
*   **WebSocket**: Canal de comunicação bidirecional persistente.
*   **Where Clause**: Filtro SQL.
*   **While Loop**: Loop enquanto condição for verdadeira.
*   **White Space**: Espaço em branco (tab, espaço). Significativo em Python.
*   **Widget**: Componente de interface.
*   **Wildcard**: Coringa (`*`).
*   **Window**: Objeto global no navegador.
*   **Wireframe**: Esboço da interface.
*   **Worker**: Processo que executa tarefas (Gunicorn Workers).
*   **Workflow**: Fluxo de trabalho.
*   **Workspace**: Espaço de trabalho.
*   **Wrapper**: Função que embrulha outra.
*   **Write**: Gravar.
*   **WSGI (Web Server Gateway Interface)**: Padrão Python para comunicação entre Servidor Web e Aplicação Flask.

## X
*   **XSS**: Cross Site Scripting.
*   **HTML/XML**: Linguagens de marcação.

## Y
*   **YAML**: Yet Another Markup Language. Usado no `docker-compose.yml`.
*   **Yield**: Palavra-chave para geradores em Python.

## Z
*   **Zero-Day**: Vulnerabilidade descoberta antes de existir correção.
*   **Zip**: Compressão.
*   **Zone**: Zona DNS ou Timezone.

---
**Nota**: Esta lista cobre os principais termos que podem surgir numa conversa técnica de nível pleno/sênior sobre o projeto.
