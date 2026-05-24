"""Script temporario para inspecionar as colunas do CSV e corrigir o parser."""
import pandas as pd
import io
import re

CSV_PATH = r'planilnhas_externas\sistema_academico_utfpr\Alunos_bolsistas_todos_fevereiro_2026.csv'

with open(CSV_PATH, 'rb') as f:
    raw = f.read().decode('latin-1')

df = pd.read_csv(io.StringIO(raw), sep=';', dtype=str, on_bad_lines='skip')
df.columns = [re.sub(r'["\s]+', ' ', c).strip().strip('"').strip() for c in df.columns]

print("=== COLUNAS LIMPAS ===")
for i, col in enumerate(df.columns):
    print(f"  [{i:02d}] {col!r}")

print()
print("=== PRIMEIRA LINHA DE DADOS ===")
first = df.iloc[0]
for col in df.columns:
    val = re.sub(r'["\s]+', ' ', str(first[col])).strip().strip('"').strip()
    print(f"  {col!r:28} -> {val!r}")
