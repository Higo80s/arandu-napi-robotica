# Segurança, Governança e Cibersegurança

**Data:** Janeiro/2026
**Classificação:** Confidencial / Uso Interno
**Escopo:** Proteção de Dados de Bolsistas e Segurança da Aplicação

---

## 1. Princípios de Segurança da Informação
Este sistema processa dados pessoais sensíveis (CPF, Dados Bancários, Histórico Acadêmico). A segurança não é uma *feature*, é um requisito legal (LGPD) e ético.

### 1.1 Camadas de Proteção
1.  **Transporte:** O uso de HTTPS (TLS 1.2+) é **obrigatório** em produção.
2.  **Aplicação (WAF):** Validação estrita de input via WTForms previne XSS (Cross-Site Scripting).
3.  **Banco de Dados:** Consultas parametrizadas via SQLAlchemy anulam Risco de SQL Injection (OWASP Top 10).

---

## 2. Governança de Dados e LGPD

### 2.1 Ciclo de Vida do Dado
- **Coleta:** Apenas dados estritamente necessários para o pagamento de bolsas são coletados (Minimização).
- **Processamento:** Ocorre em servidor institucional (On-Premise), garantindo soberania dos dados.
- **Descarte:** Dados de bolsistas inativos por >5 anos devem ser anonimizados (Roadmap V7).

### 2.2 Controle de Acesso (RBAC)
Atualmente, o sistema opera em modo "Admin Único" ou "Autenticação LDAP Integrada" (dependendo do deploy).
- **Risco:** Contas compartilhadas.
- **Mitigação Atual:** Logs de acesso do servidor web.
- **Ação Futura:** Implementar Roles (Admin, Coordenador, Auditor).

---

## 3. Vulnerabilidades e Mitigações (Análise Crítica)

| Vulnerabilidade | Risco | Status | Mitigação |
| :--- | :--- | :--- | :--- |
| **SQL Injection** | Crítico | ✅ Mitigado | Uso exclusivo de ORM. Proibido SQL cru (`text()`) com concatenação. |
| **CSRF** | Alto | ✅ Mitigado | Tokens CSRF (`Flask-WTF`) em todos os formulários POST. |
| **Session Hijacking** | Médio | ⚠️ Atenção | Cookies devem ter flags `Secure` e `HttpOnly` no deploy. |
| **Insegurança de Infra** | Alto | ⚠️ Atenção | Servidor Windows não deve expor porta 5003 publicamente. Usar Proxy Reverso (Nginx/IIS). |

---

## 4. Plano de Resposta a Incidentes

### Em caso de vazamento de dados:
1.  **Isolamento:** Desconectar servidor da rede `editais-server`.
2.  **Análise:** Logs de acesso (`nginx.log` ou `waitress console`).
3.  **Comunicação:** Notificar DPO da UTFPR em até 24h.

---

## 5. Recomendações para a Equipe de TI

### Políticas de Backup
- **Frequência:** Diária (Incremental), Semanal (Full).
- **Armazenamento:** Local + Remoto (Criptografado).
- **Teste de Restore:** Trimestral. *Backup não testado não existe.*

### Governança de Código
- Todo commit na `main` deve passar por Code Review.
- Credenciais de banco de dados **nunca** devem ser commitadas (usar `.env`).

---

*Este documento deve ser revisado anualmente ou após atualizações maiores de versão.*
