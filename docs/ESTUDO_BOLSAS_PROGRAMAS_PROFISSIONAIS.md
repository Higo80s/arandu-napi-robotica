# Estudo de Viabilidade Técnico e Negocial: Módulo de Fomento para Programas Profissionais

**Data:** Fevereiro de 2026
**Objetivo:** Analisar a viabilidade e propor uma solução arquitetural para o gerenciamento e a visibilidade das bolsas/auxílios concedidos no âmbito dos **Programas de Pós-Graduação Profissionais (Mestrado e Doutorado)**.

---

## 1. Contexto e Problema de Negócio

Historicamente, o sistema de Gestão de Editais foi desenhado com foco nos fomentos institucionais governamentais, especialmente **CAPES (PROAP)** e **CNPq**, cujo fluxo é vertical e controlado pela PROPPG. 

Os **Programas Profissionais (MP e DP)**, por sua natureza, não recebem rotineiramente as cotas PROAP convencionais. Seus recursos provêm de:
- **Captação Própria**: Parcerias de P&D (Pesquisa e Desenvolvimento) com a iniciativa privada.
- **Editais Estaduais Específicos**: Fundação Araucária (PR).
- **Fundações de Apoio**: Ex. FUNTEF.
- **Isenções ou Auxílios Internos**.

**O Desafio:** Os coordenadores desses programas geram valor enorme através da captação de recursos privados/externos, mas esses dados ficam ocultos nas métricas institucionais caso o sistema exija fluxos burocráticos engessados desenhados para a CAPES. Precisamos **dar visibilidade a esse esforço**, tratando os dados de forma assertiva.

---

## 2. Análise da Arquitetura Atual (Viabilidade)

Do ponto de vista técnico e de banco de dados, o sistema atual (**V25**) está altamente maduro e já suporta a estrutura necessária **sem necessidade de refatorações complexas**.

### O que já temos pronto no Banco de Dados (`models.py`):
- **Identificação do Programa:** A tabela `ProgramaAcademico` já possui a coluna `tipo_oferta` (`'Acadêmico'` vs `'Profissional'`).
- **Agências Flexíveis:** A tabela `AgenciaFomento` foi externalizada na Fase 22. É possível cadastrar empresas (ex: Renault, Copel) ou fundações (FUNTEF) como agências de fomento institucionais ou privadas.
- **Vínculo Flexível:** O `Edital` pode ter um `orcamento_total`, o fluxo de rodadas de seleção (Fase 10) e já suporta `bolsistas` recebendo valores diferenciados.

**Conclusão da Viabilidade:** **Alta viabilidade técnica.** Não é necessário criar novas tabelas isoladas para os profissionais. A solução ideal é construir **Visualizações e Fluxos de Interface** (Submódulos) sobre o Core existente.

---

## 3. Proposta de Solução: Submódulo "Fomento Profissional / Captação P&D"

Para preservar o "padrão de trabalho do sistema", propomos as seguintes intervenções organizadas em um novo submódulo ágil:

### A. Fluxo de Captação e Registro (Coordenadores)
1. **Nova Categoria de Agência:** Permitir o cadastro de tipo de Agência como "Privada (Empresa)", "Fundação de Apoio" e "Agência Reguladora (ANEEL/ANP)".
2. **Edital / Acordo de Parceria:** Em vez de chamar estritamente de "Edital 01/2026", o sistema permitirá usar a entidade `Edital` para registrar "Acordo P&D Empresa X" ou "Convênio FUNTEF nº 123", definindo o Orçamento Total captado.
3. **Módulo de Projetos (Aproveitamento da Fase 10):** Permitir que o projeto P&D aprovado pelo coordenador profissional se conecte a bolsas cadastradas no sistema.

### B. Visibilidade e Governança (PROPPG / Direções)
1. **Aba Exclusiva em Gestão de Editais:** Criar uma aba ou tela separada (ex: `/editais/parcerias-profissionais`) para organizar visualmente o que é fomento institucional governamental vs captação externa.
2. **KPIs no Dashboard Estratégico:** 
   - No atual painel `/dashboard/estrategico`, deve-se criar um "Card" e um Gráfico exclusivos de **"Volume de Recursos Captados na Iniciativa Privada (Programas Profissionais)"**. 
   - Hoje o dashboard foca na quantidade de bolsas; para programas profissionais, o *valor monetário captado (R$)* é um indicador primário de sucesso muito forte.
3. **Relatórios Consolidados:** O filtro de geração de relatórios (ex: Relatório SUCUPIRA) já inclui os bolsistas da casa. Precisamos incluir a flag "Tipo de Oferta" nos outputs PDF/Excel.

---

## 4. Próximos Passos (Plano de Ação)

Caso a PROPPG esteja de acordo com essa abordagem de aproveitamento do core de dados, os próximos passos do lado do desenvolvimento seriam:

1. **Backend / Roteamento:** Criar um atalho nas rotas (`/bolsistas/profissionais`) que liste automaticamente todos os bolsistas cujos programas tenham `tipo_oferta == 'Profissional'`.
2. **Dashboard de Captação:** Implementar a querry no SQLAlchemy `sum(Edital.orcamento_total)` filtrado por Agências de Categoria Privada, populando o dashboard corporativo.
3. **UI/UX Menu:** Adicionar a categoria "Captação de Fomento (MP/DP)" no menu lateral esquerdo sob a seção de Relatórios ou Gestão.

---
*Este estudo serve como ponto de partida para aprovação visual e lógica da funcionalidade. A implementação exigirá de 1 a 2 dias focados na interface web (Jinja/Templates) e controllers (Rotas).*
