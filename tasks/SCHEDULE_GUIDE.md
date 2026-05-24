# 📅 Como Agendar a Verificação de Bolsas no Windows

Para que o sistema envie e-mails automaticamente todos os dias, você deve usar o **Agendador de Tarefas do Windows**.

## Passo a Passo

1. Abra o menu Iniciar e digite **Agendador de Tarefas**.
2. No painel direito, clique em **Criar Tarefa Básica...**.
3. **Nome:** `GestaoEditais_VerificarBolsas`
4. **Disparador:** Selecione **Diariamente**.
   - Defina o horário (Sugerido: 08:00:00).
5. **Ação:** Selecione **Iniciar um programa**.

### Configuração do Programa

* **Programa/Script:** (Caminho para o python no seu ambiente virtual)
  - Se estiver usando o ambiente virtual `.venv`, procure algo como:
  `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\.venv\Scripts\python.exe`
  - Se não estiver usando venv, use apenas `python` (mas garanta que é o python onde as libs estão instaladas).

* **Adicione argumentos (opcional):**
  `tasks/check_expiring.py`

* **Iniciar em (obrigatório):**
  `C:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo`
  *(A pasta raiz do projeto)*

6. Clique em **Concluir**.

## Testando
No Agendador, clique com o botão direito na tarefa criada e selecione **Executar**. Verifique se o e-mail chegou (ou se o log apareceu, caso esteja testando localmente).

---
**Nota:** Lembre-se de configurar as credenciais reais de e-mail no arquivo `.env` para que os envios funcionem de verdade.
