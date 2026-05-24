# Módulo de Diversidade e Inclusão Social
**Documento Descritivo e Estratégico**

## 1. Contextualização: Dados Confiáveis, mas "Cegos Socialmente"
Até a implementação deste módulo, o Sistema de Gestão de Editais operava com excelência na gestão administrativa e financeira das bolsas. Os dados eram **altamente confiáveis** do ponto de vista contábil e processual: sabíamos exatamente *quantas* bolsas foram concedidas, *quais* os valores, vigências e programas beneficiados.

No entanto, o sistema sofria de uma **"cegueira social"**. Ele respondia com precisão "quanto se gasta" e "quem recebe" (CPF/Nome), mas era incapaz de responder **"quem é o sujeito"** por trás do benefício. O sistema não enxergava se os recursos estavam chegando a mulheres, negros, indígenas, quilombolas ou pessoas com deficiência. Essa lacuna tornava impossível avaliar a efetividade das políticas de ações afirmativas na pós-graduação.

## 2. Objetivos do Módulo
O Módulo de Diversidade foi criado para transformar o sistema de uma ferramenta puramente administrativa para um instrumento de **Gestão Sociopolítica Baseada em Evidências**.

**Objetivos Primários:**
*   **Visibilidade:** Dar luz aos grupos historicamente sub-representados no ecossistema de pesquisa e pós-graduação.
*   **Monitoramento:** Acompanhar em tempo real a evolução da representatividade de gênero, raça/cor e grupos específicos (quilombolas, PcD, primeira geração).
*   **Indução:** Fornecer dados para que os Programas de Pós-Graduação (PPGs) possam desenhar suas próprias políticas de inclusão.

## 3. Histórico e Perceção da Necessidade
A necessidade emergiu da compreensão de que a "neutralidade" dos dados administrativos mascarava desigualdades estruturais. A percepção foi impulsionada por:
1.  **Demandas Institucionais e Legais:** A necessidade de responder a órgãos de controle e à sociedade sobre a aplicação das cotas e ações afirmativas.
2.  **Gap de Informação:** A dificuldade da PROPPG em gerar relatórios simples sobre questões raciais ou de gênero sem recorrer a cruzamentos manuais complexos ou dados imprecisos de outros sistemas.

### Integração Técnica
A integração foi realizada de forma cirúrgica para não impactar a operação diária, mas garantindo profundidade na coleta:
*   **Modelagem de Dados:** Expansão do modelo `DadosSociais` para incluir campos sensíveis como orientação sexual, autodeclaração quilombola (com nome da comunidade) e o indicador de "primeira geração no ensino superior" (vital para medir mobilidade social).
*   **Interface Humanizada:** Atualização dos formulários de cadastro (`bolsistas/form.html`) com linguagem inclusiva e respeitosa.
*   **Visualização Estratégica:** Criação de um Dashboard exclusivo (`/diversidade`), separado das visões financeiras, para dar destaque e solenidade e esses indicadores.

## 4. Colaboração com Políticas Públicas
O sistema agora se torna um **ativo estratégico** para a formulação de políticas:

1.  **Diagnóstico Preciso:** Permite identificar quais programas (PPGs) avançaram na inclusão e quais ainda são "bolhas" de exclusão.
2.  **Alocação de Recursos (Fomento Indutor):** Futuros editais podem usar os indicadores do dashboard para premiar programas mais diversos com cotas adicionais de bolsas (fator de indução).
3.  **Defesa de Orçamento:** Dados concretos sobre o impacto social das bolsas (ex: atendendo primeira geração de universitários) são argumentos poderosos na defesa da manutenção e ampliação do financiamento público.

## 5. O Novo Cenário do Sistema
Com a entrega deste módulo, o sistema evolui para um **Repositório de Inteligência Social**.

**Como fica a base de informações:**
*   **Multidimensionalidade:** Cada bolsista agora é visto em sua totalidade (Acadêmica + Financeira + Social).
*   **Transparência Ativa:** O dashboard converte dados brutos em narrativa visual, permitindo que gestores identifiquem gargalos (ex: "efeito tesoura" na carreira de mulheres cientistas) instantaneamente.
*   **Fim da Invisibilidade:** Grupos como quilombolas e PcD, antes invisíveis estatisticamente na base de pagamentos, agora possuem contagem e visibilidade próprias.

O sistema deixa de ser apenas um "pagador de bolsas" para ser um "sensor" da realidade social da pós-graduação da universidade.
