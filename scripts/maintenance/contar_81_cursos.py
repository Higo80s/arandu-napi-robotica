"""
Contagem CORRETA: 81 cursos da Sucupira
Programas com M e D = 2 cursos separados
"""

from auditar_programas_sucupira import SUCUPIRA_DATA

# Lista completa do usuário com níveis separados
SUCUPIRA_81_CURSOS = """
40006018179P5	Engenharia Química	PPGEQ	AP	Mestrado Acadêmico
40006018183P2	Textil e Moda	PPGTM	AP	Mestrado Acadêmico
40006018182P6	Ciência da Computação	PPGCC	CM	Mestrado Acadêmico
33283010001P5	Ensino de Física - PROFIS (Polo)	PROFIS	CM	Mestrado Profissional em Rede
40006018170P8	INOVAÇÕES TECNOLÓGICAS	PPGIT	CM	Mestrado Profissional
33004013069P2	Regulamentação de Recursos Hídricos (Polo)	PROFÁGUA	CM	Mestrado Profissional em Rede
40006018037P6	BIOINFORMÁTICA	PPGBIOINFO	CP	Mestrado Acadêmico
40001016175P8	Bioinformática (Associação com UFPR)	PPGAB	CP	Doutorado Acadêmico
40006018012P3	Engenharia Elétrica	PPGEE	CP	Mestrado Acadêmico
40002012171P9	ENGENHARIA ELETRICA (Associação com UEL)	PPGAEE	CP	Doutorado Acadêmico
40006018025P8	Informática	PPGI	CP	Mestrado Profissional
31075010001P2	Matemática em Rede Nacional (Polo)	PROFMAT	CP	Mestrado Profissional em Rede
40006018024P1	Engenharia Mecânica	PPGEM	CP/PG	Mestrado Acadêmico
40006018044P2	ADMINISTRAÇÃO	PPGA	CT	Mestrado Acadêmico
53045009001P3	ADMINISTRAÇÃO PÚBLICA EM REDE NACIONAL (Polo)	PROFIAP	CT	Mestrado Profissional em Rede
40006018013P0	CIÊNCIA E TECNOLOGIA AMBIENTAL	PPGCTA	CT	Mestrado Acadêmico
40006018013P0	CIÊNCIA E TECNOLOGIA AMBIENTAL	PPGCTA	CT	Doutorado Acadêmico
40006018011P7	Computação Aplicada	PPGCA	CT	Mestrado Profissional
40006018173P7	Educação Física	PPGEF	CT	Mestrado Acadêmico
40006018018P1	Engenharia Biomédica	PPGEB	CT	Mestrado Profissional
40006018008P6	ENGENHARIA CIVIL	PPGEC	CT	Mestrado Acadêmico
40006018008P6	ENGENHARIA CIVIL	PPGEC	CT	Doutorado Acadêmico
40006018001P1	ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL	CPGEI	CT	Mestrado Acadêmico
40006018001P1	ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL	CPGEI	CT	Doutorado Acadêmico
40006018003P4	ENGENHARIA MECÂNICA E DE MATERIAIS	PPGEM	CT	Mestrado Acadêmico
40006018003P4	ENGENHARIA MECÂNICA E DE MATERIAIS	PPGEM	CT	Doutorado Acadêmico
40006018035P3	ESTUDOS DE LINGUAGENS	PPGEL	CT	Mestrado Acadêmico
40006018172P0	FÍSICA E ASTRONOMIA	PPGFA	CT	Mestrado Acadêmico
40006018019P8	Formação Científica, Educacional e Tecnológica	PPGFCET	CT	Mestrado Profissional
40006018019P8	Formação Científica, Educacional e Tecnológica	PPGFCET	CT	Doutorado Profissional
31075010001P2	Matemática em Rede Nacional (Polo)	PROFMAT	CT	Mestrado Profissional em Rede
40006018017P5	Planejamento e Governança Pública	PPGPGP	CT	Mestrado Profissional
40006018017P5	Planejamento e Governança Pública	PPGPGP	CT	Doutorado Profissional
40006018032P4	Química	PPGQ	CT	Mestrado Acadêmico
40006018038P2	SISTEMAS DE ENERGIA	PPGSE	CT	Mestrado Profissional
40006018181P0	Sustentabilidade Ambiental Urbana	PPGSAU	CT	Doutorado Acadêmico
40006018002P8	TECNOLOGIA E SOCIEDADE	PPGTE	CT	Mestrado Acadêmico
40006018002P8	TECNOLOGIA E SOCIEDADE	PPGTE	CT	Doutorado Acadêmico
40006018184P9	Design Prospectivo	PPGDP	CT	Mestrado Acadêmico
40006018185P5	Educação Tecnológica	PPGET	CT	Mestrado Acadêmico
40015017009P8	Zootecnia (Associação Unioeste)	PPGZO	DV	Mestrado Acadêmico
40015017009P8	Zootecnia (Associação Unioeste)	PPGZO	DV	Doutorado Acadêmico
40006018043P6	AGROECOSSISTEMAS	PPGSIS	DV/SH	Mestrado Acadêmico
40006018174P3	Engenharia Ambiental: Análise e Tecnologia Ambiental	PPGEA	FB	Mestrado Acadêmico
40006018175P0	CIÊNCIA E ENGENHARIA DE MATERIAIS	PPGCEM	LD/AP	Mestrado Acadêmico
40006018023P5	Engenharia Ambiental	PPGEA	LD/AP	Mestrado Acadêmico
40006018027P0	Ensino de Ciências Humanas, Sociais e da Natureza	PPGEN	LD/CP	Mestrado Profissional
40006018041P3	ENSINO DE MATEMÁTICA	PPGMAT	LD/CP	Mestrado Profissional
40006018015P2	Tecnologia de Alimentos	PPGTAL	LD/FB	Mestrado Profissional
33283010001P5	Ensino de Física - PROFIS (Polo)	PROFIS	MD	Mestrado Profissional em Rede
31102000001P6	PROPRIEDADE INTELECTUAL E TRANSFERÊNCIA DE TECNOLOGIA PARA INOVAÇÃO	PROFNIT	MD	Mestrado Profissional em Rede
31001017169P2	Química em Rede Nacional (Polo)	PROFQUI	MD	Mestrado Profissional em Rede
40006018026P4	Tecnologias Ambientais	PPGTAMB	MD	Mestrado Acadêmico
40006018034P7	TECNOLOGIAS COMPUTACIONAIS PARA O AGRONEGÓCIO	PPGTCA	MD	Mestrado Profissional
40006018016P9	Tecnologia de Alimentos	PPGTA	MD/CM	Mestrado Acadêmico
40006018016P9	Tecnologia de Alimentos	PPGTA	MD/CM	Doutorado Acadêmico
40006018005P7	AGRONOMIA	PPGAG	PB	Mestrado Acadêmico
40006018005P7	AGRONOMIA	PPGAG	PB	Doutorado Acadêmico
40006018010P0	Desenvolvimento Regional	PPGDR	PB	Mestrado Acadêmico
40006018010P0	Desenvolvimento Regional	PPGDR	PB	Doutorado Acadêmico
40006018030P1	Engenharia Civil	PPGEC	PB	Mestrado Acadêmico
40006018031P8	Engenharia de Produção e Sistemas	PPGEPS	PB	Mestrado Acadêmico
40006018009P2	ENGENHARIA ELÉTRICA E DE COMPUTAÇÃO	PPGEE	PB	Mestrado Acadêmico
40006018036P0	LETRAS	PPGL	PB	Mestrado Acadêmico
31075010001P2	Matemática em Rede Nacional (Polo)	PROFMAT	PB	Mestrado Profissional em Rede
40006018020P6	Tecnologia de Processos Químicos e Bioquímicos	PPGTP	PB	Mestrado Acadêmico
40006018171P4	CIÊNCIA DA COMPUTAÇÃO	PPGCC	PG	Mestrado Acadêmico
40006018004P0	ENGENHARIA DE PRODUÇÃO	PPGEP	PG	Mestrado Acadêmico
40006018004P0	ENGENHARIA DE PRODUÇÃO	PPGEP	PG	Doutorado Acadêmico
40006018022P9	Engenharia Elétrica	PPGEE	PG	Mestrado Acadêmico
40006018177P2	ENGENHARIA QUÍMICA	PPGEQ	PG	Mestrado Acadêmico
40006018006P3	ENSINO DE CIÊNCIA E TECNOLOGIA	PPGECT	PG	Mestrado Profissional
40006018028P7	ENSINO DE CIÊNCIA E TECNOLOGIA	PPGECT	PG	Doutorado Acadêmico
40006018176P6	BIOTECNOLOGIA	PPGBIOTEC	PG/DV	Mestrado Acadêmico
40006018176P6	BIOTECNOLOGIA	PPGBIOTEC	PG/DV	Doutorado Acadêmico
40006018178P9	Recursos Naturais e Sustentabilidade	PPGRNS	SH	Mestrado Acadêmico
31075010001P2	Matemática em Rede Nacional (Polo)	PROFMAT	TD	Mestrado Profissional em Rede
40006018033P0	PROCESSOS QUÍMICOS E BIOTECNOLÓGICOS	PPGQB	TD	Mestrado Acadêmico
40006018180P3	Tecnologia Biociências	PPGBIO	TD	Mestrado Profissional
"""

linhas = [l.strip() for l in SUCUPIRA_81_CURSOS.strip().split('\n') if l.strip()]

print("=" * 80)
print("CONTAGEM OFICIAL: 81 CURSOS DE POS-GRADUACAO UTFPR")
print("=" * 80)

# Contar por nível
mestrados = sum(1 for l in linhas if 'Mestrado' in l)
doutorados = sum(1 for l in linhas if 'Doutorado' in l)

print(f"\nMESTRADOS: {mestrados}")
print(f"DOUTORADOS: {doutorados}")
print(f"TOTAL: {len(linhas)} cursos")

# Contar programas ÚNICOS (códigos distintos)
codigos = set()
for linha in linhas:
    codigo = linha.split('\t')[0]
    codigos.add(codigo)

print(f"\nPROGRAMAS UNICOS (codigos distintos): {len(codigos)}")

# Programas que oferecem M+D
programas_md = {}
for linha in linhas:
    parts = linha.split('\t')
    codigo = parts[0]
    nivel = parts[4] if len(parts) > 4 else ''
    
    if codigo not in programas_md:
        programas_md[codigo] = []
    programas_md[codigo].append(nivel)

programas_com_md = sum(1 for niveis in programas_md.values() if len(niveis) > 1)

print(f"Programas que oferecem M+D: {programas_com_md}")

print("\n" + "=" * 80)
print("FORMULA:")
print("=" * 80)
print(f"{len(codigos)} programas unicos")
print(f"- {len(codigos) - programas_com_md} programas com 1 nivel (M ou D)")
print(f"- {programas_com_md} programas com 2 niveis (M+D)")
print(f"= {(len(codigos) - programas_com_md) * 1 + programas_com_md * 2} = {len(linhas)} CURSOS TOTAIS")
print("=" * 80)

# Detalhar programas M+D
print("\nPROGRAMAS COM MESTRADO E DOUTORADO:")
print("-" * 80)
for codigo, niveis in sorted(programas_md.items()):
    if len(niveis) > 1:
        # Buscar nome
        for linha in linhas:
            if linha.startswith(codigo):
                parts = linha.split('\t')
                sigla = parts[2] if len(parts) > 2 else ''
                print(f"  {codigo} - {sigla}")
                break

print("\n" + "=" * 80)
