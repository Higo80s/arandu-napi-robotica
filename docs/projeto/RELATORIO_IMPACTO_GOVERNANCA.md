# Relatório de Impacto, Governança e Expansão
**Sistema de Gestão de Editais e Bolsas (SGEB)**

> **Status**: Em Produção (Piloto) | **Versão**: 7.0 | **Tecnologia**: Python/Flask

---

## 1. Análise Geral de Uso
O Sistema de Gestão de Editais e Bolsas (SGEB) foi desenvolvido para sanar uma lacuna crítica na administração da Pró-Reitoria de Pesquisa e Pós-Graduação (PROPPG): a **ausência de ferramentas centralizadas** para o controle financeiro e temporal de bolsas acadêmicas.

### Cenário Anterior (O Problema)
*   **Gestão fragmentada**: Uso de planilhas Excel desconexas, propensas a erro humano.
*   **Risco de Compliance**: Dificuldade em controlar vigências (bolsas pagas indevidamente após o prazo ou finalizadas prematuramente).
*   **Baixa Rastreabilidade**: Impossibilidade de auditar quem autorizou qual pagamento.

### Resultados Atuais (A Solução)
O sistema centraliza 100% do ciclo de vida das bolsas:
1.  **Mapeamento de Editais**: Cadastro estruturado de regras financeiras e prazos.
2.  **Controle de "Vagas"**: Visualização imediata de cotas ocupadas vs. disponíveis.
3.  **Segurança Jurídica**: Validação automática de datas (Início do Curso vs Início da Bolsa vs Duração Máxima).

---

## 2. Funcionalidades e Capacidades (O que o sistema faz)

Este software não é apenas um "cadastro", é um **motor de regras de negócio**.

### A. Gestão Financeira e Prazos
O sistema impede erros administrativos comuns através de validação estrita:
*   **Cálculo Automático de Vigência**: Ao inserir o início da bolsa e a duração, o sistema projeta a data final exata.
*   **Gestão de Afastamentos**: Se um aluno entra em licença-maternidade, o sistema re-calcula o fim da bolsa automaticamente, garantindo o direito da bolsista sem esforço manual.

### B. Relatórios Gerenciais (Governança)
Geração de artefatos oficiais em PDF e Excel para tomada de decisão:
*   **Folha de Pagamento**: Relatório mensal consolidado para o financeiro.
*   **Previsão Orçamentária**: Projeção de gastos futuros baseada nos contratos ativos.
*   **Termos de Compromisso**: Geração automática de documentos legais.

### C. Dashboard em Tempo Real
*(Espaço reservado para Print do Dashboard)*
> **Sugestão**: Inserir aqui visualização dos gráficos de distribuição de bolsas por modalidade.

---

## 3. Contribuição para Governança de Dados (PROPPG)

A implementação institucional deste sistema é um pilar para a **Governança de Dados** da universidade:

1.  **Padronização**: Define uma ontologia única para "Modalidades", "Níveis" e "Status". Acaba com a dúvida se "Dr." é o mesmo que "Doutorado".
2.  **Qualidade do Dado**: Regras de validação na entrada (Input Validation) impedem que dados "sujos" (ex: datas impossíveis, valores negativos) entrem na base.
3.  **Auditabilidade**: Histórico de alterações permite saber a evolução de cada processo seletivo.

**Impacto no Planejamento Estratégico**:
Com dados confiáveis, a PROPPG pode responder perguntas como:
*   *"Qual o custo médio por aluno de Doutorado?"*
*   *"Qual a taxa de evasão de bolsistas por programa?"*
*   *"Temos saldo orçamentário para abrir um novo edital emergencial?"*

---

## 4. Potencial de Expansão (O "Produto" para outras IFES)

O cenário da UTFPR não é único. A grande maioria das Instituições Federais de Ensino Superior (IFES) carece de sistemas de nicho para gestão fina de bolsas, dependendo de módulos genéricos de ERPs (como o SIGAA) que muitas vezes não atendem às especificidades de editais de fomento estaduais/locais.

### Por que este sistema é exportável?
1.  **Agnóstico de Banco de Dados**: Desenvolvido com SQLAlchemy, pode rodar em SQLite (pequenas instituições), PostgreSQL (padrão open-source) ou Oracle (padrão corporativo federal).
2.  **Regras de Negócio Parametrizáveis**: As regras de "Duração Máxima", "Valor" e "Nível" são cadastradas no banco, não "chumbadas" no código. Isso permite que outra universidade use o mesmo sistema apenas cadastrando seus próprios editais.
3.  **Baixo Custo de Infraestrutura**: Pode rodar em containers leves (Docker), exigindo poucos recursos de hardware.

### Estratégia de Compartilhamento
*   **Modelo Open Source Federal**: Disponibilização no Portal do Software Público Brasileiro.
*   **Colaboração Interinstitucional**: Parceria com outras UTFPRs ou IFPRs para co-desenvolvimento.

---

## 5. Próximos Passos e Ajustes Necessários

Para atingir esse nível de maturidade institucional, o sistema requer:
1.  **Integração LDAP/SAML**: Para uso do login único institucional.
2.  **Logs de Auditoria Granulares**: Registro detalhado de IPs e ações.
3.  **Documentação de API**: Caso outros sistemas (ex: Portal da Transparência) precisem consumir dados deste sistema.

---
**Conclusão**: O SGEB está pronto para deixar de ser uma ferramenta departamental e se tornar um ativo institucional, provendo inteligência de dados e segurança operacional para a gestão pública.
