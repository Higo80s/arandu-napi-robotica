# Relatório de Planejamento e Atualização (2026)

Este documento apresenta as estratégias para evolução do Sistema de Gestão de Editais, abordando expansão de funcionalidades, segurança, internacionalização e infraestrutura.

---

## 1. Monitoramento de Egressos (Item A)
**Objetivo:** Acompanhar a trajetória profissional dos ex-bolsistas.

**Estratégia de Implementação:**
1.  **Formulário Público:** Criar uma rota pública `/egresso/atualizar` onde o ex-aluno acessa via CPF e Data de Nascimento.
2.  **Dados Coletados:**
    -   Situação profissional atual (Empregado, Pesquisador, Docente, etc.).
    -   Faixa salarial (dados anonimizados para estatística).
    -   Relevância da bolsa na carreira (Escala Likert 1-5).
    -   Localização atual (País/Estado).
3.  **Fluxo de Convite:** Disparo automático de e-mail 6, 12 e 24 meses após o fim da vigência da bolsa com o link único.

## 2. Internacionalização e Refugiados (Item B)
**Objetivo:** Expandir o módulo de internacionalização para incluir dados humanitários.

**Dados Necessários para Refugiados:**
-   **País de Origem:** Para mapeamento geopolítico.
-   **Status Legal:** (Solicitante de Refúgio, Refugiado Reconhecido, Visto Humanitário).
-   **Idioma Materno:** Para suporte linguístico.
-   **Necessidades Específicas:** Apoio psicológico, moradia, validação de diploma.

**Ação Imediata:**
-   Adicionar campos na tabela `DadosSociais` ou criar tabela `DadosHumanitarios`.
-   Gerar relatório específico para a Pró-Reitoria de Relações Internacionais.

## 3. Executável e Portabilidade (Item C)
**Objetivo:** Rodar o sistema em outros computadores sem configurar Python manualmente.

**Solução:** Utilizar **PyInstaller**.
-   **Comando:** `pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py`
-   **Banco de Dados:** O SQLite (`gestao_editais_new.db`) é um arquivo. Basta copiar junto com o executável.
-   **Limitação:** Se usar PostgreSQL, o banco precisa ser instalado/acessado externamente. Para portabilidade total, manter SQLite na versão "Portable".

## 4. Nuvem e Rede Compartilhada (Item D)
**Objetivo:** Compartilhar o banco de dados entre múltiplos usuários em tempo real.

**Proposta:**
1.  **Hospedagem:** PythonAnywhere (já configurado) ou Render/Railway.
2.  **Banco de Dados:** Migrar definitivamente para PostgreSQL (Supabase ou Neon gratuitos para redes pequenas).
3.  **Rede:** O acesso deixa de ser local (`127.0.0.1`) e passa a ser via URL (`https://gestao-editais.utfpr.edu.br`).
4.  **Vantagem:** Fim dos conflitos de arquivo SQLite bloqueado por múltiplos acessos.

## 5. Segurança do Sistema (Item E)
**Estado Atual:**
-   **Autenticação:** Uso de `Flask-Login` com sessões seguras.
-   **Senhas:** Hash com `werkzeug.security` (PBKDF2/SHA256). Nenhuma senha é salva em texto puro.
-   **Proteção:** `CSRF Protect` ativado nos formulários.

**Níveis de Segurança Adicionais (Recomendado):**
1.  **2FA (Autenticação de Dois Fatores):** Exigir código via e-mail/app para login de administradores.
2.  **Logs de Auditoria:** Já implementado (`audit.py`), registrando quem fez o que.
3.  **Rate Limiting:** Bloquear IP após 5 tentativas falhas de login (usar `Flask-Limiter`).
4.  **Backup Criptografado:** Garantir que os backups do banco não sejam legíveis sem chave.

## 6. Uso do Figma (Item F)
**Análise:** O Figma é essencial para *prototipagem* antes de codificar.
-   **Como usar:** Desenhar as telas novas (ex: Portal do Egresso) no Figma para validar com a PROPPG antes de gastar horas programando.
-   **Vantagem:** Evita refação de código. Facilita aprovação visual.

## 7. Vídeo Curso (Item G)
**Proposta:** Sim, é possível e recomendável.
-   **Estrutura do Curso:**
    -   Módulo 1: Cadastro de Editais e Cotas.
    -   Módulo 2: Gestão de Bolsistas e Pagamentos.
    -   Módulo 3: Relatórios e Auditoria.
    -   Módulo 4: Administrativo (Usuários/Configurações).
-   **Ferramentas:** OBS Studio para captura de tela + Edição simples. Posso gerar o *roteiro* detalhado para cada vídeo.

## 8. Patente e Propriedade Intelectual (Item H)
**Processo de Registro de Programa de Computador (INPI):**
1.  **Sigilo:** Manter o código fonte em repositório privado até o registro.
2.  **Hash do Código:** Gerar um resumo criptográfico (SHA-256) de todo o código fonte para provar integridade e data de criação.
3.  **Documentação:** Gerar PDF com os trechos principais do código (`app.py`, `models.py`) e telas do sistema.
4.  **Titularidade:** Definir se pertence à UTFPR ou ao desenvolvedor (depende do contrato de bolsa/trabalho).

## 9. Estrutura do Sistema (Item I)
**Arquitetura Atual (MVC - Flask):**
-   **Backend:** Python/Flask. Dividido em `Blueprints` (módulos):
    -   `auth`: Login/Logout.
    -   `dashboard`: Gráficos e APIs.
    -   `reports`: Geração de PDFs e Excel.
    -   `bolsistas`: CRUD de discentes.
-   **Banco de Dados:** SQLAlchemy ORM (abstrato). Atualmente suporta SQLite (dev) e PostgreSQL (prod).
-   **Frontend:** HTML5 + Jinja2 (Templates) + CSS Vanilla (Bootstrap like).
-   **Segurança:** Decorators `@login_required` e `@admin_required` protegem rotas.

## 10. Cadastro de Novos Usuários (Item J)
**Estado Atual:** Não existe rota pública de cadastro ("Sign Up").
**Como fazer hoje:** Apenas Administradores podem criar usuários diretamente no banco de dados ou via interface administrativa (se habilitada).
**Recomendação:** Criar rota `/admin/usuarios/novo` visível apenas para usuários com role "ADMIN", para convidar novos gestores.

## 11. Área de Coordenadores (Item K)
**Plano de Implementação:**
1.  **Novo Perfil de Usuário:** Criar role `COORDENADOR`.
2.  **Vínculo:** Na tabela `User`, adicionar campo `programa_id`.
3.  **Filtragem Global:**
    -   No `app.py`, todas as queries de `Bolsista` devem verificar:
        -   `if current_user.role == 'COORDENADOR': query = query.filter_by(programa_id=current_user.programa_id)`
4.  **Dashboard Personalizado:** Ao logar, o coordenador vê apenas os gráficos e saldos do SEU programa.

---
**Data:** 07/02/2026
**Responsável:** Assistente de Desenvolvimento (Agentic AI)
