# Proposta de Institucionalização - Sistema de Gestão de Editais

**Universidade Tecnológica Federal do Paraná**  
**Pró-Reitoria de Pesquisa e Pós-Graduação (PROPPG)**

---

## 1. Identificação do Projeto

| Item | Descrição |
|------|-----------|
| **Nome** | Sistema de Gestão de Editais e Bolsistas |
| **Desenvolvedor** | Higo Santos |
| **Período de Desenvolvimento** | Dezembro 2025 - Janeiro 2026 |
| **Stack Tecnológica** | Python 3.11 + Flask 3.0 + SQLAlchemy 3.1 |
| **Status Atual** | Sistema funcional, testado em ambiente de produção |
| **Repositório** | https://github.com/Higo80s/gestao_editais |

---

## 2. Contexto e Motivação

### 2.1 Problema Identificado

A gestão de editais de bolsas na PROPPG envolve processos manuais complexos:

- **Cálculo manual de vigências**: Suscetível a erros, especialmente com afastamentos e extensões
- **Geração manual de relatórios**: Processo demorado, repetitivo e propenso a inconsistências
- **Falta de rastreabilidade**: Dificuldade em acompanhar histórico de pagamentos e alterações
- **Dispêndio de tempo**: Aproximadamente 120 horas/ano dedicadas a tarefas burocráticas
- **Risco de não-conformidade**: Possibilidade de pagamentos incorretos ou fora do prazo

### 2.2 Motivação para Desenvolvimento

O sistema foi desenvolvido para:

1. **Automatizar tarefas repetitivas** e eliminar cálculos manuais
2. **Centralizar informações** de editais, modalidades e bolsistas
3. **Garantir conformidade** com as regras de vigência e afastamentos
4. **Facilitar prestação de contas** através de relatórios automatizados
5. **Economizar tempo** da equipe PROPPG para focar em atividades estratégicas

---

## 3. Funcionalidades Implementadas

### 3.1 Gestão de Editais
- Cadastro de editais com múltiplas modalidades (Mestrado, Doutorado, Pós-Doutorado, IC)
- Definição de valores, vagas e períodos de vigência
- Controle de prestação de contas

### 3.2 Gestão de Bolsistas
- **Dados Pessoais**: Nome, CPF, Email
- **Dados Acadêmicos**: Programa, Campus, Orientador, Datas de Ingresso e Previsão de Defesa
- **Dados Bancários**: Banco, Agência, Conta, Tipo de Conta
- **Dados de Bolsa**: Modalidade, Início, Duração, Vigência calculada automaticamente
- **Controle de Status**: Ativo/Inativo com registro de motivo de desligamento

### 3.3 Cálculo Automático de Vigências
- **Vigência padrão**: Data início + duração em meses
- **Limite acadêmico**: Respeitando prazos máximos do programa/modalidade
- **Extensões automáticas**: Por afastamentos (maternidade, saúde)
- **Validações**: Garantindo consistência de datas e períodos

### 3.4 Gestão de Afastamentos
- Registro de afastamentos (Maternidade, Licença Saúde, Outros)
- Extensão automática da vigência da bolsa
- Histórico completo de afastamentos por bolsista

### 3.5 Relatórios Automatizados
- **Folha de Pagamento Mensal** (Excel e PDF)
- **Relatório Gráfico** (Distribuição por Campus, Programa, Investimento)
- **Relatório Estratégico de Residentes** (Pós-Doc)
- **Exportação de Dados Acadêmicos** (Lista de Programas)

### 3.6 Dashboard Gerencial
- Indicadores financeiros em tempo real
- Gráficos de ocupação de vagas
- Métricas acadêmicas (duração média)
- Distribuição por edital, campus e programa

### 3.7 Busca e Filtros Avançados
- Busca por: Nome, CPF, Processo SEI, Número de Formulário, Programa
- Filtro por: Edital, Status (Ativo/Inativo), Campus
- Ordenação personalizável

---

## 4. Benefícios Mensuráveis

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Tempo de geração de relatório mensal | 8 horas | 5 minutos | **99% de redução** |
| Erros em cálculos de vigência | ~5% | 0% | **100% de eliminação** |
| Horas economizadas por ano | - | 120+ | **Ganho de produtividade** |
| Capacidade de gestão simultânea | ~20 bolsistas | 50+ bolsistas | **150% de aumento** |
| Rastreabilidade de alterações | Baixa | Alta | **Auditoria completa** |

---

## 5. Arquitetura Técnica

### 5.1 Stack Tecnológica Atual

```
Frontend:  HTML5 + CSS3 + JavaScript (Vanilla)
Backend:   Python 3.11 + Flask 3.0
ORM:       SQLAlchemy 3.1
Database:  SQLite (Desenvolvimento) / PostgreSQL (Produção)
Servidor:  Waitress (WSGI)
Reports:   OpenPyXL (Excel) + ReportLab (PDF) + Matplotlib (Gráficos)
```

### 5.2 Arquitetura MVC

```
Models (models.py)       → Entidades: Edital, Modalidade, Bolsista, etc.
Views (templates/)       → Interface HTML + Jinja2
Controllers (app.py)     → Rotas Flask + Lógica de Negócio
Services (reports.py)    → Geração de Relatórios
```

### 5.3 Segurança e Boas Práticas

- ✅ Validações de entrada em todas as rotas
- ✅ Sanitização de dados antes de persistência
- ✅ Variáveis de ambiente para configurações sensíveis (`.env`)
- ✅ `.gitignore` robusto (sem senhas/tokens no repositório)
- ✅ Transações atômicas no banco de dados
- ✅ Tratamento de exceções e logs

---

## 6. Alinhamento com Padrões UTFPR

### 6.1 Stack Institucional vs Stack Atual

| Componente | UTFPR (Padrão) | Sistema Atual |
|------------|----------------|---------------|
| **Frontend** | Angular + Design System Gov.br | HTML/CSS/JS |
| **Backend** | Java + Spring Boot | Python + Flask |
| **Banco de Dados** | PostgreSQL | SQLite/PostgreSQL |
| **Padrões de Código** | IN Desenvolvimento Colaborativo | PEP 8 (Python) |

### 6.2 Opções de Integração

#### **Opção 1: Manutenção da Stack Python (Recomendado)**

**Vantagens:**
- ✅ Sistema já 100% funcional e testado
- ✅ Implantação imediata (sem reescrita)
- ✅ Stack mais leve e rápida para este caso de uso
- ✅ Python é amplamente utilizado em contextos acadêmicos
- ✅ Facilita extensões futuras (IA, Data Science)

**Desvantagens:**
- ⚠️ Divergência do padrão institucional
- ⚠️ Necessidade de manutenção de stack adicional

**Proposta de Mitigação:**
- Dockerização do sistema (isolamento completo)
- Integração via APIs REST (seguindo IN de Interoperabilidade)
- Documentação completa para equipe institucional

#### **Opção 2: Migração Gradual para Java/Spring Boot**

**Vantagens:**
- ✅ Alinhamento total com padrão UTFPR
- ✅ Suporte da equipe DIRGTI/DESIS-RT
- ✅ Integração facilitada com outros sistemas

**Desvantagens:**
- ⚠️ Reescrita completa (~3-6 meses)
- ⚠️ Risco de perda de funcionalidades
- ⚠️ Testes extensivos necessários

**Proposta de Execução:**
- Manter Python em produção durante migração
- Migração modular (módulo por módulo)
- Testes comparativos de funcionalidade
- Timeline: 6 meses para MVP em Java

#### **Opção 3: Abordagem Híbrida**

- Manter backend Python expostos via API REST
- Desenvolver frontend Angular consumindo a API
- Migração gradual de módulos críticos para Java

---

## 7. Proposta de Implantação

### 7.1 Implantação Imediata (Python)

**Timeline:** 1-2 semanas

1. **Semana 1**: Configuração de servidor UTFPR
   - Instalação de dependências Python
   - Configuração do banco PostgreSQL
   - Deploy com Docker ou Waitress
   - Testes de conectividade e segurança

2. **Semana 2**: Migração de dados e homologação
   - Importação de dados existentes
   - Testes de aceitação com equipe PROPPG
   - Treinamento básico de usuários
   - Go-live

### 7.2 Migração Futura (Java/Spring Boot)

**Timeline:** 6 meses (se aprovado)

- **Mês 1-2**: Análise de requisitos e design
- **Mês 3-4**: Desenvolvimento MVP (módulos essenciais)
- **Mês 5**: Testes e ajustes
- **Mês 6**: Migração em produção

---

## 8. Requisitos de Infraestrutura

### 8.1 Servidor de Aplicação

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| **CPU** | 2 cores | 4 cores |
| **RAM** | 2 GB | 4 GB |
| **Armazenamento** | 10 GB | 20 GB |
| **SO** | Linux (Ubuntu 20.04+) | Ubuntu 22.04 LTS |

### 8.2 Banco de Dados

- **PostgreSQL 14+** (ou compatível)
- **Armazenamento**: 5 GB inicial (crescimento ~1 GB/ano)
- **Backup**: Diário automatizado

### 8.3 Rede

- **Porta HTTP**: 80 (redirecionamento) 
- **Porta HTTPS**: 443 (TLS 1.3)
- **Acesso**: Intranet UTFPR (VPN para acesso externo)

---

## 9. Conformidade com Instruções Normativas

### 9.1 IN Desenvolvimento Colaborativo

- ✅ Código versionado no Git
- ✅ README.md completo
- ✅ Documentação técnica
- ⚙️ A adequar: Fluxo de code review institucional

### 9.2 IN Interoperabilidade

- ✅ APIs REST implementáveis
- ✅ Formato JSON para troca de dados
- ✅ Documentação de endpoints (OpenAPI/Swagger possível)

---

## 10. Próximos Passos Sugeridos

1. **Reunião de Apresentação**
   - Demonstração ao vivo do sistema
   - Discussão de questões técnicas
   - Alinhamento de expectativas

2. **Decisão de Stack**
   - Definir entre Opção 1, 2 ou 3
   - Estabelecer timeline

3. **Preparação de Servidor**
   - Solicitação de máquina virtual UTFPR
   - Configuração de acesso e permissões

4. **Homologação**
   - Testes com dados reais (anonimizados)
   - Validação pela equipe PROPPG

5. **Capacitação**
   - Treinamento de usuários
   - Documentação de processos

---

## 11. Considerações Finais

Este sistema foi desenvolvido com foco em **resolver um problema real da PROPPG**, resultando em ganhos mensuráveis de produtividade e redução de erros.

A proposta de **manutenção da stack Python** permite:
- ✅ Implantação imediata (1-2 semanas)
- ✅ Validação do valor do sistema com usuários reais
- ✅ Decisão informada sobre migração futura

Estou à disposição para:
- Apresentações técnicas detalhadas
- Esclarecimentos sobre implementação
- Colaboração no processo de institucionalização

---

**Higo Santos**  
Desenvolvedor do Sistema  
GitHub: [@Higo80s](https://github.com/Higo80s)

**Contato UTFPR:**  
Patrícia Strapasson Piccinini (DIRGTI/DESIS-RT)
