# 📅 Como Agendar a Verificação de Bolsas no Windows

Para que o sistema envie e-mails automaticamente todos os dias, você deve usar o **Agendador de Tarefas do Windows**.

## Instalação recomendada (silenciosa)

Na raiz do projeto, execute:

```powershell
.\scripts\recriar_agendamentos_silenciosos.ps1
```

Esse comando cria ou atualiza todos os agendamentos sem janela preta e **remove
os aliases antigos** deste repo (`Arandu_PagamentoBolsas_Nuvem`,
`Arandu_AvisoUltimoMesBolsa`, `Arandu_CobrancaRelatorioFinal`,
`Arandu_ResumoDiario`). Não mexe em tarefas `AranduProppg_*`. Cada tarefa
mostra somente um resumo no canto inferior direito, com descrição humana,
quantidade `(00)`/`(01)` e destinatário quando aplicável. Os detalhes ficam em
`logs\cron_*.log`.

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

## Pagamento de Bolsas → Nuvem (dia 20)

Envia automaticamente a folha Excel de **Pagamento de Bolsas** (competência do mês corrente) para a pasta `/05_pagamentos` na Nuvem UTFPR e confirma por e-mail.

1. **Nome:** `AranduRobotica_PagamentoBolsasNuvem`
2. **Disparador:** Diariamente às **08:15** (a tarefa só executa no **dia 20**).
3. **Programa:** `C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\tasks\run_enviar_pagamento_bolsas.bat`
4. **Iniciar em:** pasta raiz do projeto.

**Teste manual (qualquer data):**
```bat
flask enviar-pagamento-bolsas --mes 2026-05 --forcar
```

Texto editável e envio sob demanda em **E-mails → Pagamento de bolsas** (`/admin/config-pagamento-bolsas`).
Visão geral das automações: **E-mails → Central de automações** (`/admin/automacoes`).

Variáveis no `.env`: `CLOUD_WEBDAV_URL`, `CLOUD_USER`, `CLOUD_PASSWORD`, `CLOUD_PAGAMENTOS_FOLDER`, `PAGAMENTO_BOLSAS_EMAIL`, `MAIL_*`.

---

## Resumo diário (tarefas + alertas)

Envia por e-mail a lista de tarefas pendentes em `/anotacoes/` e o resumo dos alertas (Ações Pendentes).

1. **Nome:** `AranduRobotica_ResumoDiario`
2. **Disparador:** Diariamente às **08:00**.
3. **Programa:** `C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\tasks\run_resumo_diario.bat`
4. **Iniciar em:** pasta raiz do projeto.

**Teste manual (sem enviar e-mail):**
```bat
flask send-daily-digest --dry-run
```

**Envio real:**
```bat
flask send-daily-digest
```

Destinatário: `NOTIFICATION_EMAIL` no `.env` (fallback: `MAIL_USERNAME`).

---

## Cobrança relatório final (bolsistas desligados)

- **No desligamento:** e-mail imediato para bolsista + orientador/supervisor.
- **Todo dia 15:** mesmo e-mail + resumo para a equipe Robótica (só se houver pendências).
- **Para:** marque **Relatório Final Entregue** no Checkout e salve o cadastro.

1. **Nome:** `AranduRobotica_CobrancaRelatorioFinal`
2. **Disparador:** Diariamente às **08:05** (executa a cobrança mensal apenas no dia 15).
3. **Programa:** `C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\tasks\run_cobranca_relatorio_final.bat`
4. **Iniciar em:** pasta raiz do projeto.

**Teste manual (simular dia 15):**
```bat
flask cobranca-relatorio-final --dry-run --forcar
```

**Envio real (fora do dia 15, só teste):**
```bat
flask cobranca-relatorio-final --forcar
```

Texto editável em **Administração → Cobrança Relatório Final** (`/admin/config-relatorio-final`).

---

## Aviso último mês de bolsa

Notifica **bolsista + orientador** quando a bolsa entra no mês de `data_fim_bolsa`
(status **Última Parcela**). Envio **único por competência** (YYYY-MM do fim).
Se houver avisos no dia, a equipe Robótica recebe um resumo.

1. **Nome:** `AranduRobotica_AvisoUltimoMesBolsa`
2. **Disparador:** Diariamente às **08:10**.
3. **Programa:** `C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\tasks\run_aviso_ultimo_mes_bolsa.bat`
4. **Iniciar em:** pasta raiz do projeto.

**Teste manual:**
```bat
flask aviso-ultimo-mes-bolsa --dry-run
```

**Reenvio forçado (mesmo se já notificado na competência):**
```bat
flask aviso-ultimo-mes-bolsa --forcar
flask aviso-ultimo-mes-bolsa --dry-run --forcar
```

No formulário do bolsista (admin/gestor): botão **Reenviar aviso último mês**.

Logs em **Administração → Monitor de Automação** (`/admin/monitor-automacao`), tarefa `Aviso Último Mês de Bolsa`.

Texto editável em **Administração → Aviso Último Mês** (`/admin/config-ultimo-mes-bolsa`).

---

## Confirmação de início da bolsa

Notifica **bolsista + orientador** com datas de início/fim e quantidade de parcelas
para confirmação. Disparo principal: **Ativar Bolsista (Fundação)** (com prévia do
e-mail antes do envio) ou reenvio manual na ficha. A tarefa diária é rede de
segurança para ativos implantados que ainda não receberam o aviso
(cadastros já ativos na implantação desta rotina não são reenviados).

1. **Nome:** `AranduRobotica_ConfirmacaoInicioBolsa`
2. **Disparador:** Diariamente às **08:12**.
3. **Programa:** `C:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\tasks\run_confirmacao_inicio_bolsa.bat`
4. **Iniciar em:** pasta raiz do projeto.

**Teste manual:**
```bat
flask confirmacao-inicio-bolsa --dry-run
```

Texto e prévia em **Administração → Confirmação de Início** (`/admin/config-confirmacao-inicio`).

---
**Nota:** Lembre-se de configurar as credenciais reais de e-mail no arquivo `.env` para que os envios funcionem de verdade.
