# Guia de Contribuição - Sistema de Gestão de Editais

Obrigado pelo interesse em contribuir! Este documento fornece diretrizes para contribuir com o projeto.

---

## 🎯 Como Contribuir

### 1. Reportar Bugs

Se encontrar um bug:

1. Verifique se já não foi reportado nas [Issues](https://github.com/Higo80s/gestao_editais/issues)
2. Abra uma nova issue com:
   - Título descritivo
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Versão Python e sistema operacional

### 2. Sugerir Melhorias

Para sugerir novas funcionalidades:

1. Abra uma issue com tag `enhancement`
2. Descreva o caso de uso
3. Explique o benefício esperado
4. Proponha uma solução (opcional)

### 3. Contribuir com Código

#### Workflow de Desenvolvimento

```bash
# 1. Fork o repositório no GitHub

# 2. Clone seu fork
git clone https://github.com/SEU_USUARIO/gestao_editais.git
cd gestao_editais

# 3. Adicione o repositório original como remote
git remote add upstream https://github.com/Higo80s/gestao_editais.git

# 4. Crie uma branch para sua feature
git checkout -b feature/minha-funcionalidade

# 5. Faça suas alterações
# ... código ...

# 6. Commit suas mudanças
git add .
git commit -m "feat: adiciona funcionalidade X"

# 7. Push para seu fork
git push origin feature/minha-funcionalidade

# 8. Abra um Pull Request no GitHub
```

---

## 📋 Padrões de Código

### Python (PEP 8)

```python
# ✅ Bom
def calcular_vigencia(data_inicio, meses_duracao):
    """
    Calcula a data fim da bolsa.
    
    Args:
        data_inicio: Data de início da bolsa
        meses_duracao: Duração em meses
        
    Returns:
        Data fim calculada
    """
    from dateutil.relativedelta import relativedelta
    return data_inicio + relativedelta(months=meses_duracao)

# ❌ Ruim
def calc(d,m):
    from dateutil.relativedelta import relativedelta
    return d+relativedelta(months=m)
```

### Nomenclatura

- **Variáveis**: `snake_case` (ex: `data_inicio_bolsa`)
- **Funções**: `snake_case` (ex: `calcular_parcelas()`)
- **Classes**: `PascalCase` (ex: `BolsistaForm`)
- **Constantes**: `UPPER_CASE` (ex: `MAX_DURACAO_MESES`)

### Comentários

```python
# ✅ Bom - Explica o "porquê"
# Calcula limite acadêmico: adiciona 6 meses de tolerância
# para evitar desligamentos prematuros próximos à defesa
academic_limit_months = standard_duration + 6

# ❌ Ruim - Explica o "o quê" (óbvio no código)
# Adiciona 6 a standard_duration
academic_limit_months = standard_duration + 6
```

---

## 🧪 Testes

### Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-cov

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html
```

### Escrever Testes

```python
# tests/test_utils.py
from utils import calcular_parcelas
from datetime import date

def test_calcular_parcelas_primeiro_mes():
    """Testa cálculo de parcela no primeiro mês."""
    inicio = date(2025, 1, 15)
    referencia = date(2025, 1, 20)
    
    parcela = calcular_parcelas(inicio, referencia)
    
    assert parcela == 1

def test_calcular_parcelas_sexto_mes():
    """Testa cálculo de parcela no sexto mês."""
    inicio = date(2025, 1, 15)
    referencia = date(2025, 6, 20)
    
    parcela = calcular_parcelas(inicio, referencia)
    
    assert parcela == 6
```

---

## 📝 Mensagens de Commit

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(escopo): descrição curta

Descrição detalhada (opcional)

Refs: #123
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Apenas documentação
- `style`: Formatação (sem mudança de lógica)
- `refactor`: Refatoração de código
- `test`: Adição/correção de testes
- `chore`: Tarefas de build, CI/CD, etc.

### Exemplos

```bash
# ✅ Bom
git commit -m "feat(relatorios): adiciona relatório de residentes em PDF"

git commit -m "fix(bolsistas): corrige cálculo de vigência com afastamento

O cálculo anterior não considerava múltiplos afastamentos.
Agora soma todas as extensões corretamente.

Refs: #45"

git commit -m "docs: atualiza README com instruções de deploy"

# ❌ Ruim
git commit -m "correcoes"
git commit -m "fix stuff"
git commit -m "WIP"
```

---

## 🔍 Code Review

Pull Requests passarão por revisão. Esperamos:

- [ ] Código segue PEP 8
- [ ] Testes passando
- [ ] Documentação atualizada (se aplicável)
- [ ] Commit messages descritivos
- [ ] Sem conflitos com `main`
- [ ] Funcionalidade testada localmente

### Processo de Review

1. Mantenedor revisa o PR em até 48h
2. Solicita mudanças (se necessário)
3. Contributor faz ajustes
4. Aprovação e merge

---

## 🚀 Ambiente de Desenvolvimento

### Setup Completo

```bash
# Clone o repositório
git clone https://github.com/Higo80s/gestao_editais.git
cd gestao_editais

# Crie ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Copie .env.example para .env
cp .env.example .env

# Execute o servidor
python production.py
```

### Estrutura de Branches

- `main`: Código em produção (estável)
- `develop`: Desenvolvimento ativo (instável)
- `feature/*`: Novas funcionalidades
- `bugfix/*`: Correções urgentes
- `hotfix/*`: Correções críticas em produção

---

## 📚 Recursos Úteis

- [Documentação Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ❓ Dúvidas?

- Abra uma [issue](https://github.com/Higo80s/gestao_editais/issues) com tag `question`
- Entre em contato: GitHub [@Higo80s](https://github.com/Higo80s)

---

**Agradecemos sua contribuição! 🎉**
