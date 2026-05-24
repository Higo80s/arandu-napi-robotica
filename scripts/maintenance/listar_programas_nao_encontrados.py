"""Lista programas de mestrado não encontrados no banco"""
import sqlite3
import os

db_path = os.path.join('instance', 'gestao_editais_new.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Todos os códigos da Plataforma Sucupira - Mestrado
cotas_sucupira = {
    '40006018044P2': ('ADMINISTRAÇÃO', 4),
    '40006018043P6': ('AGROECOSSISTEMAS', 5),
    '40006018005P7': ('AGRONOMIA', 14),
    '40006018037P6': ('BIOINFORMÁTICA', 6),
    '40006018176P6': ('BIOTECNOLOGIA', 10),
    '40006018171P4': ('CIÊNCIA DA COMPUTAÇÃO', 4),
    '40006018182P6': ('CIÊNCIA DA COMPUTAÇÃO', 4),
    '40006018175P0': ('CIÊNCIA E ENGENHARIA DE MATERIAIS', 8),
    '40006018013P0': ('CIÊNCIA E TECNOLOGIA AMBIENTAL', 8),
    '40006018010P0': ('Desenvolvimento Regional', 14),
    '40006018173P7': ('Educação Física', 4),
    '40006018023P5': ('Engenharia Ambiental', 8),
    '40006018174P3': ('Engenharia Ambiental: Análise e Tecnologia Ambiental', 5),
    '40006018008P6': ('ENGENHARIA CIVIL', 13),
    '40006018030P1': ('Engenharia Civil (PPGEC)', 5),
    '40006018004P0': ('ENGENHARIA DE PRODUÇÃO', 13),
    '40006018031P8': ('Engenharia de Produção e Sistemas (PPGEPS)', 5),
    '40006018022P9': ('Engenharia Elétrica', 8),
    '40006018012P3': ('Engenharia Elétrica - Cornélio Procópio', 10),
    '40006018009P2': ('Engenharia Elétrica e de Computação', 5),
    '40006018001P1': ('ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL', 0),
    '40006018024P1': ('Engenharia Mecânica', 5),
    '40006018029P3': ('Engenharia Mecânica', 0),
    '40006018003P4': ('ENGENHARIA MECÂNICA E DE MATERIAIS', 12),
    '40006018177P2': ('ENGENHARIA QUÍMICA', 4),
    '40006018179P5': ('ENGENHARIA QUÍMICA', 5),
    '40006018035P3': ('ESTUDOS DE LINGUAGENS', 6),
    '40006018172P0': ('FÍSICA E ASTRONOMIA', 4),
    '40006018036P0': ('LETRAS', 8),
    '40006018033P0': ('PROCESSOS QUÍMICOS E BIOTECNOLÓGICOS', 5),
    '40006018032P4': ('Química', 4),
    '40006018178P9': ('RECURSOS NATURAIS E SUSTENTABILIDADE', 5),
    '40006018016P9': ('Tecnologia de Alimentos', 10),
    '40006018020P6': ('Tecnologia de Processos Químicos e Bioquímicos', 4),
    '40006018002P8': ('TECNOLOGIA E SOCIEDADE', 14),
    '40006018026P4': ('Tecnologias Ambientais', 8),
    '40006018034P7': ('TECNOLOGIAS COMPUTACIONAIS PARA O AGRONEGÓCIO', 6),
    '40006018183P2': ('TÊXTIL E MODA', 2),
    '40006018014P6': ('Zootecnia', 0),
}

print("=" * 80)
print("PROGRAMAS DE MESTRADO NÃO ENCONTRADOS NO BANCO")
print("=" * 80)

nao_encontrados = []

for codigo, (nome, qtd) in cotas_sucupira.items():
    cur.execute("SELECT id, sigla_programa FROM programa_academico WHERE codigo_programa = ?", (codigo,))
    prog = cur.fetchone()
    
    if not prog:
        nao_encontrados.append((codigo, nome, qtd))

conn.close()

if nao_encontrados:
    print(f"\nTotal: {len(nao_encontrados)} programas\n")
    for i, (codigo, nome, qtd) in enumerate(nao_encontrados, 1):
        print(f"{i:2}. {codigo} - {nome}")
        print(f"    Bolsas: {qtd}")
        print()
else:
    print("\n✅ Todos os programas foram encontrados!")

print("=" * 80)
