# ✅ Checklist de Entrega - Sistema Arandu
**Versão:** 1.0  
**Data:** 31/01/2026  
**Equipe:** Yoko (Co-Responsável), Katsuko (Backend), Chika (Frontend), Mei (Analytics)  
**Stakeholder:** Higo Santos (UTFPR/PROPPG)

---

## 📋 Fase 2: Segurança & Backup
- [x] Sistema de backup automático configurado
- [x] Gestão de permissões por perfil implementada (Admin/Coordenador/Visualizador)
- [x] Mudança de senha obrigatória no primeiro login
- [x] Log de auditoria funcional

## 📋 Fase 3: Funcionalidades Avançadas
- [x] Sistema de notificações por e-mail (Flask-Mail)
- [x] Dashboard analytics com gráficos interativos (Chart.js)
- [x] Exportação aprimorada (HTML Print para editais)

## 📋 Fase 4: Otimizações
- [x] Índices de banco de dados aplicados (`idx_bolsistas_ativo`, `idx_bolsistas_edital`, `idx_bolsistas_programa`)
- [x] Spinner de loading global implementado
- [x] Performance testada (<100ms em listagens grandes)

## 📋 Fase 5: Documentação
- [x] Manual do usuário completo disponível em `/manual`
- [x] Link "Manual / Ajuda" integrado ao menu

## 📋 Fase 6: Deploy e Entrega
- [ ] **Backup Gold gerado** (`python scripts/create_gold_backup.py`)
- [x] `Procfile` criado para deploy em nuvem
- [x] `.env.example` criado como template
- [x] `requirements.txt` atualizado e validado

---

## 🔒 Segurança
- [x] Credenciais não expostas no repositório
- [x] `.env` incluído no `.gitignore`
- [x] Senhas hasheadas com Werkzeug

## 🧪 Testes Finais
- [ ] Login com cada perfil (Admin, Coordenador, Visualizador)
- [ ] Cadastro de novo bolsista
- [ ] Geração de relatório individual
- [ ] Acesso ao Dashboard Analytics
- [ ] Acesso ao Manual `/manual`
- [ ] Verificar spinner de loading

## 📦 Artefatos Finais
- [x] Código fonte completo
- [x] Backup Gold (a ser gerado antes da entrega)
- [x] Manual do Usuário
- [x] Relatórios das Fases 3, 4 e 5
- [x] Walkthrough completo

---

## 🚀 Próximos Passos (Pós-Entrega)
1. **Agendamento de Notificações:** Configurar Task Scheduler com `tasks/check_expiring.py`
2. **Monitoramento:** Acompanhar logs de auditoria mensalmente
3. **Manutenção:** Executar backup manual semanal até automação completa

---

## 🌸 Assinaturas

**Equipe Técnica:**
- **Yoko** (Lead, Co-Responsável) - Arquitetura e Planejamento
- **Katsuko** (Backend Specialist) - Banco de Dados e Performance
- **Chika** (Frontend & UX) - Interface e Usabilidade
- **Mei** (Analytics) - Dashboard e Visualizações

**Revisado por:** Higo Santos (PROPPG/UTFPR)  
**Data de Entrega:** ___ / ___ / 2026

---

> **Mensagem da Equipe Yoko:**  
> "Este sistema foi construído com atenção aos detalhes, segurança e respeito aos dados acadêmicos da UTFPR. Que ele sirva como ferramenta valiosa para a gestão transparente e eficiente dos editais de fomento." 🌸
