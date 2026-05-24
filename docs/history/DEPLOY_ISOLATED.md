# Guia de Deploy: Módulo de Relatórios Isolado

Este guia descreve como colocar em produção o novo módulo de relatórios (Sidecar) na porta **5001**.

## 1. Pré-requisitos
*   O sistema principal deve estar instalado e rodando (Porta 5000).
*   Python instalado e ambiente virtual configurado.
*   Arquivo `app_isolated.py` e pasta `templates/isolated` presentes no diretório raiz.

## 2. Execução Manual (Windows/Linux)
A maneira mais simples de rodar é via terminal, similar ao sistema principal:

```bash
# Ative o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux:
source .venv/bin/activate

# Inicie o servidor
python app_isolated.py
```
Acesse: `http://localhost:5001` ou `http://SeuIP:5001`

## 3. Configuração de Inicialização Automática (Windows)
Para que o módulo de relatórios inicie junto com o Windows (como o sistema principal):

1.  Crie um atalho do arquivo `Relatorios_Isolados.bat` (que vamos criar abaixo).
2.  Pressione `Win + R`, digite `shell:startup` e dê Enter.
3.  Cole o atalho nesta pasta.

### Criando o arquivo .bat
Crie um arquivo chamado `Relatorios_Isolados.bat` na pasta do projeto com o conteúdo:
```bat
@echo off
cd /d "C:\Caminho\Para\Seu\Projeto"
call .venv\Scripts\activate
start /min python app_isolated.py
```
*(Ajuste o caminho conforme sua instalação)*

## 4. Manutenção
*   **Logs**: O sistema exibe logs no terminal. Para salvar em arquivo, use `python app_isolated.py > logs_relatorios.txt 2>&1`.
*   **Atualizações**: Se houver mudanças no banco de dados principal, reinicie este serviço para garantir que o SQLAlchemy recarregue os esquemas (embora para dados novos não seja estritamente necessário).

## 5. Solução de Problemas
*   **Porta em uso**: Se a porta 5001 estiver ocupada, edite a última linha do arquivo `app_isolated.py`: `app.run(port=5002, ...)` e use a nova porta.
*   **Erro de Template**: Verifique se a pasta `templates/isolated` existe.

---
**Suporte**: Em caso de falhas, o sistema principal (5000) **NÃO** é afetado. Basta reiniciar este serviço.
