# Relatório Técnico: Integração e Sincronização da Base Oficial UTFPR

## 1. Visão Geral
Este relatório detalha a implementação do módulo de Integração de Dados CSV ("Alunos Bolsistas Todos") ao sistema *Gestão de Editais*. O objetivo central foi projetar um mecanismo capaz de manter paridade automática entre a situação real do fomento na PROPPG/UTFPR e o banco de dados local da aplicação, protegendo contra vazamentos de orçamento (Bolsas Ativas pós-defesa) e garantindo a qualidade da informação.

---

## 2. Números Comparativos e Impacto da Execução

A primeira grande carga de sincronização processou **634 registros oficiais** e os reconciliou contra o Banco de Dados vivo do sistema (PostgreSQL).

| Métrica | Resultado | Significado Estratégico |
| :--- | :--- | :--- |
| **Registros Analisados** | 634 | Total bruto de linhas lidas com sucesso do extrato CSV da UTFPR. |
| **Registros Atualizados (Upsert)** | 337 | Bolsistas que já existiam no sistema e tiveram seus perfis enriquecidos de forma automática (inserção do e-mail, correção do fomento, ou recebimento do novo Registro Acadêmico - RA). |
| **Novos Cadastrados** | 245 | Alunos inseridos do zero na base, já mapeados corretamente de acordo com as Modalidades (Mestrado, Doutorado) para o Edital Vigente principal. |
| **Bolsas Encerradas (Trava Defesa)** | 52 | **Métrica Crítica:** 52 bolsas que constariam como "Ativas" foram imediatamente baixadas e marcadas com a flag "Defesa Antecipada" devido a data de defesa preenchida, cessando o passivo com a CAPES/agência de fomento. |

---

## 3. Achados Relevantes (Descobertas Técnicas)

Durante a engenharia e execução do importador, algumas barreiras fundamentais foram encontradas e resolvidas:

1. **A Barreira Criptográfica do CPF:**
   - *O Problema:* O banco de dados do sistema utiliza criptografia em nível de aplicação (Application-Level Encryption) via `EncryptedString` para dados sensíveis. A pesquisa padrão (`Bolsista.query.filter_by(cpf=...)`) estava falhando silenciosamente no CSV porque o texto puro do CSV não casava com o Hash encriptado.
   - *A Solução:* Desenvolvemos um Algoritmo em Memória. O sistema agora carrega a frota estritamente na memória volátil, processando o *Match* do CPF descriptografado de maneira segura, sem comprometer a arquitetura de segurança (LGPD).

2. **Divergência de Formatação (Human-Error):**
   - *O Problema:* A planilha oficial expõe CPFs apenas com dígitos (ex: `08207360909`), enquanto o banco local, gerado por telas UI, guardava as máscaras (ex: `082.073.609-09`).
   - *A Solução:* Foi embarcado um sanitizador e formatador bidirecional no motor de sincronismo. Ele conserta os dados que entram para garantir que as buscas de integridade não dupliquem registros por falta de um "hífen".

3. **Arquitetura de Limpeza de Aspas:**
   - O *parser* puro do Python estava inserindo valores literais de aspas duplas `"Data"` dentro do modelo, o que inviabilizava o parseamento do Tempo (`datetime`). Um polidor interno para toda e qualquer célula lida do CSV foi ativado, garantindo sanitização completa da *String*.

---

## 4. Decisões Impactadas pelo Desenvolvimento

Em virtude das descobertas durante o fluxo, a arquitetura de dados e da UI foram adaptadas permanentemente:

- **Evolução do Schema do Banco de Dados:**
  - Foi criada uma migração estrutural no PostgreSQL para criar a coluna `registro_academico (RA)`. Esta decisão tira a carga do CPF como única âncora de dados no futuro, permitindo tracking internacional limpo.
  
- **Desacoplamento e Interface UI Assíncrona:**
  - Originalmente imaginou-se que a sincronização seria guiada via Terminal apenas por Devs. 
  - *Decisão Impactada:* Construímos um botão proeminente **"Sincronizar UTFPR (CSV)"** diretamente na tela de listagem de Discentes (UI). Qualquer Administrador no futuro pode subir a respectiva tabela atualizada e ver o *flash log* rodando, democratizando e agilizando a governança dos dados do setor.

---

## 5. Passos Futuros (Next Steps)

Com a arquitetura consolidada, os próximos marcos estratégicos recomendados são:

1. **Histórico de Auditoria Sincronizada:**
   - Criar uma tabela-log que guarde quem apertou o botão de Sincronizar, quando e com qual arquivo, mantendo o histórico corporativo intacto para auditorias internas da PROPPG.
2. **Alertas de Inconsistência Crítica:**
   - Adicionar uma regra no script de importação: Se um aluno for detectado como "INATIVO" no CSV, mas o banco Gestão Editais listar a cota como "AGENDADA" (ainda sem iniciar), um e-mail silencioso deve ser enviado ao Coordenador com a ressalva "Possível abandono prévio".
3. **Gestão do "Fomento Fantasma":**
   - Atualmente mapeamos fomentos legados como *CAPES-DS, UTFPR/Recursos Próprios2020*. Caso fontes inteiramente alienígenas e novas (ex: "*Edital Petrobras 2027*") comecem a figurar nas colunas de extração, precisamos instruir a interface a notificar *"Foi encotrada uma Fonte Desconhecida, por favor mapeie no Dicionário"*.

---
*(Relatório Técnico gerado durante as sessões de Refatoração Arquitetural V2 - Fev/2026)*
