# ROTEIRO DE APRESENTAÇÃO: SISTEMA DE GESTÃO DE EDITAIS (V6.0)

**Público-Alvo:** Equipe Técnica, Pesquisadores, Administrativos e Gestores.
**Objetivo:** Apresentação profunda do sistema, cultura de dados e workflow completo.
**Tempo Estimado:** 30 minutos (20 min explanação + 10 min perguntas).

---

## 1. Abertura e Contextualização do Problema (5 min)

**(Slide ou Fala Inicial: "O Desafio da Gestão Manual")**

"Bom dia/boa tarde a todos.
Gostaria de começar nossa reunião com uma reflexão sobre como operávamos até pouco tempo atrás.

Imaginem o cenário:
Recebemos uma planilha de um Edital com 50 bolsas. Cada aluno tem uma data de início, um prazo de 12 ou 24 meses, pode ter uma licença maternidade no meio, um trancamento, ou uma prorrogação.
Gerenciar isso manualmente, linha por linha no Excel, funcionava quando tínhamos 5 bolsistas. Com 50 ou 100, tornou-se insustentável.

**Os Riscos que corríamos:**
1.  **Erro Humano:** Calcular prazos 'de cabeça' (ex: esquecer que fevereiro tem 28 dias ou errar a conta de meses).
2.  **Perda de Prazos:** Bolsistas recebendo a mais (prejuízo ao erário) ou a menos (prejuízo ao aluno).
3.  **Falta de Memória:** "Quem era o bolsista do Edital 02/2023?" - Essa informação ficava em e-mails antigos.

Hoje, apresento a **Versão 6.0** do nosso Sistema de Gestão, que vem para resolver definitivamente essas questões."

---

## 2. A Solução Técnica e Segurança (5 min)

**(Transição: Mostrar a Tela de Login/Dashboard)**

"O que construímos aqui não é um quebra-galho. É um **Software de Gestão** completo.

### Por que confiar no sistema?
1.  **Tecnologia de Ponta:** Usamos **Python** e **Flask**, os mesmos motores usados por grandes empresas de tecnologia, garantindo estabilidade.
2.  **Banco de Dados Relacional:** (Para os técnicos: SQL/SQLAlchemy).
    *   *Exemplo:* Antes, se escrevêssimos "Engenharia Mecânica" em uma planilha e "Eng. Mec." em outra, o computador achava que eram cursos diferentes.
    *   *Agora:* Temos uma base unificada. O sistema sabe que é o mesmo curso. Isso gera relatórios fidedignos.
3.  **Segurança e Backup:**
    *   Temos criptografia de chaves.
    *   Temos backup automático diário (Local e Nuvem). Se o computador queimar hoje, recuperamos o trabalho em minutos.

---

## 3. Demonstração Prática: O Ciclo de Vida do Bolsista (15 min)

**(Ação: Navegar no Sistema em Tempo Real)**

### Passo 1: O Edital (A Regra do Jogo)
**(Ação: Menu 'Editais' > Criar/Visualizar)**
"Tudo começa aqui. O sistema reflete a realidade burocrática.
Cadastramos o **Edital**, definimos a Agência (CAPES/CNPq) e o Projeto."

### Passo 2: As Modalidades (O Controle Financeiro)
**(Ação: Menu 'Modalidades')**
"Aqui definimos o teto.
Se o Edital diz 'Mestrado: 10 vagas a R$ 2.100,00', nós travamos isso no sistema.
Isso impede que, por engano, cadastremos 11 bolsistas ou paguemos um valor errado. O sistema blinda o gestor contra erros administrativos."

### Passo 3: O Bolsista (O Coração da V6)
**(Ação: Menu 'Bolsistas' > Novo)**
"Vejam a riqueza de detalhes neste formulário. Destaco as novidades da V6:

*   **Busca por Processo SEI e Número de Formulário:** Atendendo a pedidos, agora rastreamos o processo físico. Se você digitar 'PROD-1234' na busca, vai achar a pasta física em segundos.
*   **Vínculo com Programa (V5):** Selecionamos o Campus e o Programa de uma lista padronizada. Sem erros de digitação.

**(Ação: Preencher dados fictícios de datas)**

**O Grande Diferencial: Validação de Prazos (Regime de Competência)**
Prestem atenção aqui. Vou tentar fazer algo 'errado' de propósito:
*   Vou colocar o Início da Bolsa *antes* do Início do Curso.
*   *(Ao tentar salvar)*: O sistema bloqueia! 'Erro: Início da Bolsa não pode ser anterior ao Curso'.
*   Vou tentar dar 30 meses de bolsa para um Mestrado (que só permite 24).
*   *(Ao tentar salvar)*: Bloqueado! 'Erro: Excede o limite da modalidade'.

Isso, colegas, é segurança jurídica. O sistema não deixa a gente errar."

### Passo 4: Afastamentos e Recálculos
**(Ação: Editar um bolsista > Aba Afastamentos)**
"E se a bolsista engravidar? Ou precisar trancar por saúde?
Antes, pegávamos o calendário e contávamos dias nos dedos.
Agora: Lançamos 'Licença Maternidade - 120 dias'.
O sistema **recalcula automaticamente** a nova data final da bolsa. Simples assim."

### Passo 5: Relatórios e Transparência
**(Ação: Ir para Dashboard ou Relatórios)**
"No final do mês, para fechar a folha:
Um clique em 'Gerar Excel'. Temos a lista pronta para o Financeiro.
No Dashboard, vemos quem está **'Finalizando'** (marcado em amarelo). O sistema nos avisa: 'Atenção, a bolsa de Fulano acaba este mês'."

---

## 4. O Futuro e Manutenção (3 min)

"Para encerrar a exposição técnica.
Este sistema é 'Vivo'. Ele foi feito para evoluir.
A **Documentação** (Manuais, Roteiros) foi totalmente reescrita hoje. Qualquer novo estagiário que entrar na equipe consegue aprender a usar o sistema lendo o PDF que geramos.

Os códigos também foram comentados didaticamente. Se no futuro quisermos adicionar, por exemplo, 'Integração com WhatsApp', a base está pronta."

---

## 5. Sessão de Perguntas e Respostas (Aberto)

**(Sugestão de tópicos para puxar discussão caso ninguém fale)**

1.  *"Alguém tem dúvida sobre como lançar os bolsistas do edital antigo?"*
2.  *"O que vocês acharam da nova busca pelo Número do Formulário?"*
3.  *"Querem ver como fazemos o backup na prática?"*

**(Encerramento)**
"Obrigado pela atenção. O sistema está disponível no endereço X e conto com o feedback de todos para as próximas versões."
