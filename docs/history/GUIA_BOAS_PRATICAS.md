# Guia de Boas Práticas e Segurança
## Gestão de Editais - Versão Produção

Este guia orienta sobre como manter a segurança dos seus dados e como realizar alterações no sistema sem riscos.

---

### 1. Rotina de Backup (Segurança)

Foi criado um atalho na sua Área de Trabalho chamado **"Realizar Backup"**.
Use-o da seguinte forma:

*   **Frequência:** Execute pelo menos **uma vez por semana** ou **antes de qualquer alteração importante**.
*   **O que ele faz:** Cria um arquivo ZIP contendo **TUDO** (banco de dados, arquivos do sistema, configurações).
*   **Onde fica:** Os arquivos ZIP são salvos na pasta `backups` dentro do projeto.
*   **Recomendação Extra:** Periodicamente, copie esses arquivos ZIP para um **Google Drive, Pen Drive ou HD Externo** para garantir proteção contra falhas no computador.

---

### 2. Como Fazer Alterações (Workflow de Desenvolvimento)

Como o sistema está em "Modo de Produção" (janela oculta), você **NÃO** deve editar os arquivos diretamente enquanto ele está rodando.

**Passo a Passo Seguro:**

1.  **Pare o Sistema:** Feche a janela do navegador ou reinicie o computador para garantir que nada esteja preso.
2.  **Faça um Backup:** Use o atalho "Realizar Backup".
3.  **Crie um Ambiente de Teste:**
    *   Copie a pasta inteira do projeto (`gestao_editais_novo`).
    *   Cole e renomeie para algo como `gestao_editais_TESTE`.
4.  **Trabalhe no Teste:**
    *   Abra essa nova pasta de teste.
    *   Edite o arquivo `Gestao_Editais.bat` lá e mude de `production.py` para `dev_server.py` (para ver erros na tela preta).
    *   Faça suas alterações e testes lá.
5.  **Aprovação:**
    *   Se tudo funcionar na pasta de teste, você pode copiar os **arquivos modificados** (apenas os arquivos de código `.py`, `.html`, etc., **NÃO** o banco de dados) para a pasta original de Produção.
    *   **CUIDADO:** Nunca substitua a pasta `instance` (onde fica o banco de dados) da produção pela de teste, ou você perderá dados reais acumulados.

---

### 3. Recuperação de Emergência

Se o sistema parar de funcionar:
1.  Vá na pasta `backups`.
2.  Pegue o arquivo ZIP mais recente.
3.  Extraia o conteúdo.
4.  Copie o arquivo `instance/gestao_editais_new.db` desse backup para a pasta `instance` do projeto atual.

Isso restaurará seus dados para o momento daquele backup.

---

### 4. Curiosidade: Padrões de Mercado (Como empresas fazem?)

Embora "copiar a pasta" seja seguro e simples para uso individual, empresas de software utilizam métodos mais automatizados para gerenciar o trabalho de várias pessoas ao mesmo tempo.

#### Método Profissional (Git Flow + CI/CD)
Empresas não copiam pastas. Elas usam **Controle de Versão (Git)** e servidores separados.

1.  **Branches (Ramificações):** Em vez de pastas "Teste" e "Original", existem linhas do tempo paralelas no código:
    *   `main`: Código sagrado de produção (nunca mexido diretamente).
    *   `develop`: Código de teste onde tudo se junta.
    *   `feature/nova-tela`: Onde o programador trabalha isolado.
2.  **Ambientes Segregados:**
    *   **Local:** Notebook do desenvolvedor.
    *   **Staging (Homologação):** Um servidor clone da produção apenas para testes.
    *   **Produção:** Onde o cliente acessa.
3.  **Deploy Automático:** Quando o código é aprovado, um robô copia os arquivos para o servidor automaticamente.

#### Comparativo para o seu caso
*   **Copiar Pasta (Manual):** Excelente para você agora. Visual, fácil de entender e reverter. "Se quebrar, apaga a pasta teste".
*   **Git (Profissional):** Se quiser evoluir no futuro, você pode aprender comandos como `git checkout -b` para criar ambientes de teste sem duplicar arquivos fisicamente.

