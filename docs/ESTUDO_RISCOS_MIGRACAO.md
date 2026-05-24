# Estudo de Mitigação de Riscos: Migração de Documentação (V6.2)

**Data:** Janeiro/2026
**Responsável:** Antigravity Agent
**Objetivo:** Garantir migração segura da rota `/tutorial` para `/documentacao` sem impacto sistêmico.

---

## 1. Mapeamento de Riscos

| ID | Risco Identificado | Impacto (1-5) | Probabilidade | Estratégia de Mitigação |
| :--- | :--- | :--- | :--- | :--- |
| **R01** | **Colisão de Rotas** | 5 (Crítico) | Baixa | A nova rota `/documentacao` deve ter nome de função único (`def documentacao_index`) para não colidir com `def tutorial`. O Flask falha no boot se houver colisão. |
| **R02** | **Links Quebrados (404)** | 4 (Alto) | Alta | Usuários com `/tutorial` favoritado receberão erro. **Ação:** Criar redirecionamento 301 de `/tutorial` para `/documentacao`. |
| **R03** | **Menu Inconsistente** | 3 (Médio) | Média | O `base.html` pode continuar apontando para a rota antiga se não for atualizado corretamente, ou apontar para uma rota inexistente se houver erro de digitação. |
| **R04** | **Perda de Acesso Admin** | 5 (Crítico) | Baixa | Alterações incorretas no `app.py` podem quebrar o *Application Context*, derrubando todas as rotas, inclusive `/admin`. |

---

## 2. Plano de Rollback (Reversão Imediata)

Caso a migração falhe, o seguinte protocolo deve ser executado em menos de 2 minutos:

1.  **Parar Servidor:** `taskkill /F /PID <PID_DO_FLASK>`
2.  **Restaurar Backup:**
    ```python
    # Script de Emergência prepare_rollback.py
    import shutil
    shutil.copy('app_backup_routes_2026_01_21.py', 'app.py')
    shutil.copy('templates/base_backup.html', 'templates/base.html')
    ```
3.  **Reiniciar Servidor:** `python run_server_stable.py`

---

## 3. Simulação de Cenário (Ambiente Staging)

Para validar a troca sem tocar na produção (Porta 5003), criaremos um **Ambiente de Simulação (Porta 5004)**:
1.  Duplicar `app.py` -> `app_simulation.py`.
2.  **Aplicar Mudanças:**
    *   Remover rota `/test/documentacao`.
    *   Substituir rota `/tutorial` por Redirecionamento 301.
    *   Criar rota oficial `/documentacao`.
3.  **Validar:** Acessar localhost:5004. Se sucesso, replicar código no oficial.

---

## 4. Checklist de Governança Pós-Migração
- [ ] Atualizar Manual do Usuário (screenshots antigos mostram "Tutorial").
- [ ] Monitorar logs por 24h buscando erros 404 em `/tutorial` (para garantir que o redirect funciona).
- [ ] Verificar permissões de arquivo na pasta `static/docs` (leitura para todos).
