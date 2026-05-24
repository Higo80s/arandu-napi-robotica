import sys
from app import app, db, Campus, ProgramaAcademico

RAW_DATA = """
Administração	40006018044P2	PPGA	Curitiba
Agroecossistemas	40006018043P6	PPGSIS	Dois Vizinhos
Agronomia	40006018005P7	PPGAG	Pato Branco
Agronomia	40006018005P7	PPGAG	Pato Branco
Bioinformática (associado) UTFPR/UFPR	40006018037P6	PPGAB	Cornélio Procópio
Bioinformática	40006018037P6	PPGBIOINFO	Cornélio Procópio
Biotecnologia	40006018176P6	PPGBIOTEC	dois vizinhos e ponta grossa
Ciência Da Computação -	40006018182P6	PPGCC	Campo Mourão
Ciência Da Computação -	40006018171P4	PPGCC	Ponta Grossa
Ciência E Engenharia De Materiais -	40006018175P0	PPGCEM	apucarana e londrina
Ciência E Tecnologia Ambiental	40006018013P0	PPGCTA	Curitiba
Computação Aplicada	40006018011P7	PPGCA	Curitiba
Desenvolvimento Regional -	40006018010P0	PPGDR	Pato Branco
Desenvolvimento Regional (2018) -	40006018010P0	PPGDR	Pato Branco
Educação Física - CT	40006018173P7	PPGEF	Curitiba
Engenharia Ambiental	40006018023P5	PPGEA	apucarana e londrina
Engenharia Ambiental: Análise E Tecnologia Ambiental -	40006018174P3	PPGEA	Francisco Beltrão
Engenharia Biomédica	40006018018P1	PPGEB	Curitiba
Engenharia Civil	40006018008P6	PPGEC	Curitiba
Engenharia Civil	40006018008P6	PPGEC	Curitiba
Engenharia Civil	40006018030P1	PPGEC	Pato Branco
Engenharia De Produção	40006018004P0	PPGEP	Ponta Grossa
Engenharia De Produção	40006018004P0	PPGEP	Ponta Grossa
Engenharia de Produção e Sistemas	40006018031P8	PPGEPS	Pato Branco
Engenharia Elétrica	40006018012P3	PPGEE	Cornélio Procópio
Engenharia Elétrica - Uel/Utpfr -	40002012171P9	PPGAEE	Cornélio Procópio
Engenharia Elétrica e de Computação	40006018009P2	PPGEEC	Pato Branco
Engenharia Elétrica E Informática Industrial	40006018001P1	CPGEI	Curitiba
Engenharia Elétrica E Informática Industrial	40006018001P1	CPGEI	Curitiba
Engenharia Elétrica	4006018022P9	PPGEE	Ponta Grossa
Engenharia Elétrica	4006018022P9	PPGEE	Ponta Grossa
Engenharia Mecânica - PPG	40006018024P1	PPGEM	Cornélio Procópio
Engenharia Mecânica E De Materiais - PPG	40006018003P4	PPGEM	Curitiba
Engenharia Mecânica E De Materiais - PPG	40006018003P4	PPGEM	Curitiba
Engenharia Química	40006018177P2	PPGEQ	Ponta Grossa
Engenharia Química (2019) -	40006018179P5	PPGEQ	Apucarana
Ensino De Ciência E Tecnologia	40006018028P7	PPGECT	Ponta Grossa
Ensino De Ciências Humanas, Sociais E Da Natureza	40006018027P0	PPGEN	Londrina
Ensino de Física - PROFIS	33283010001P5	MNPEF	Medianeira
Ensino De Matemática -	40006018041P3	PPGMAT	londrina e cornélio procópio
Estudos De Linguagens	40006018035P3	PPGEL	Curitiba
Física E Astronomia -	40006018172P0	PPGFA	Curitiba
Formação Científica, Educacional E Tecnológica	40006018019P8	PPGFCET	Curitiba
Formação Científica, Educacional e Tecnológica (2019) - -CT	40006018019P8	PPGFCET	Curitiba
Informática -	40006018025P8	PPGI	Cornélio Procópio
Inovações Tecnológicas	40006018170P8	PPGIT	Campo Mourão
Letras	40006018036P0	PPGL	Pato Branco
ADMINISTRAÇÃO PÚBLICA EM REDE NACIONAL	53045009001P3	PROFIAP	Multi
Ensino de Física - PROFIS	33283010001P5	MNPEF	Campo Mourão
Planejamento E Governança Pública	40006018017P5	PPGPGP	Curitiba
Planejamento E Governança Pública (2019) -	40006018017P5	PPGPGP	Curitiba
Processos Químicos e Biotecnológicos	40006018033P0	PPGQB	Toledo
GESTÃO E REGULAÇÃO DE RECURSOS HÍDRICOS - PROFÁGUA	33004013069P2	PROFÁGUA	Campo Mourão
Matemática Rede Nacional	31075010001P2	PROFMAT	Cornélio Procópio
Matemática Rede Nacional	31075010001P2	PROFMAT	Curitiba
Matemática Rede Nacional	31075010001P2	PROFMAT	Toledo
Matemática Rede Nacional	31075010001P2	PROFMAT	Pato Branco
ENSINO DE CIÊNCIA E TECNOLOGIA	40006018028P7	PPGECT	Ponta Grossa
Químíca	40006018032P4	PPGQ	Curitiba
Química Rede Nacional	31001017169P2	PROFQUI	Medianeira
Recursos Naturais e Sustentabilidade (2018) -	40006018178P9	PPGRNS	Santa Helena
Sistemas De Energia	40006018038P2	PPGSE	Curitiba
Sustentabilidade Ambiental Urbana	40006018181P0	PPGSAU	Curitiba
Tecnologia De Alimentos	40006018015P2	PPGTAL	FB/LD
Tecnologia De Alimentos	40006018016P9	PPGTA	CM-MD
Tecnologia De Processos Químicos E Bioquímicos -	40006018020P6	PPGTP	Pato Branco
Tecnologia E Sociedade	40006018002P8	PPGTE	Curitiba
Tecnologia E Sociedade -	40006018002P8	PPGTE	Curitiba
Tecnologias Ambientais -	40006018026P4	PPGTAMB	Medianeira
Tecnologias Biociências (2018) -	40006018180P3	PPGBIO	Toledo
Tecnologias Computacionais Para O Agronegócio -	40006018034P7	PPGTCA	Medianeira
Têxtil e Moda	40006018183P2	PPGTM	Apucarana
Zootecnia Associação entre Unioeste e Campus Dois Vizinhos da UTFPR do Campus Dois Vizinhos	40006018014P6	PPGZO	Dois Vizinhos
"""

def normalize_campus(name):
    n = name.lower().strip()
    if 'apucarana' in n: return 'Apucarana'
    if 'campo mourão' in n or 'campo mourao' in n or 'cm-md' in n: return 'Campo Mourão'
    if 'cornélio' in n or 'cornelio' in n: return 'Cornélio Procópio'
    if 'curitiba' in n: return 'Curitiba'
    if 'dois vizinhos' in n or 'dv' in n: return 'Dois Vizinhos'
    if 'francisco' in n or 'fb' in n: return 'Francisco Beltrão'
    if 'guarapuava' in n: return 'Guarapuava'
    if 'londrina' in n or 'fb/ld' in n: return 'Londrina' # First match for FB/LD? No, FB/LD-> FB first? 
    # FB/LD is Francisco Beltrao / Londrina.
    # List says "Tecnologia De Alimentos 40006018015P2".
    # User instructions: "curso_programa codigo sigla campus".
    # Previous I said FB, but here I mapped to Londrina if FB/LD?
    # Wait, FB is before LD alphabetically? But in string "FB/LD", F is first.
    # Let's trust the logic: if "francisco" in name -> FB. if "londrina" in name -> LD. 
    # "FB/LD" contains both? No, "FB" is not "Francisco".
    # "cm-md" -> "Campo Mourao".
    # Let's add specific shortcuts.
    
    if n == 'fb/ld': return 'Francisco Beltrão' # Pick one
    if n == 'cm-md': return 'Campo Mourão' # Pick one
    
    if 'londrina' in n: return 'Londrina'
    if 'medianeira' in n: return 'Medianeira'
    if 'pato branco' in n: return 'Pato Branco'
    if 'ponta grossa' in n: return 'Ponta Grossa'
    if 'santa helena' in n: return 'Santa Helena'
    if 'toledo' in n: return 'Toledo'
    if 'multi' in n: return 'Multi'
    return None

def main():
    with app.app_context():
        # 1. Ensure Multi Campus exists
        multi = Campus.query.filter(Campus.nome.ilike('Multi')).first()
        if not multi:
            print("Creating 'Multi' campus...")
            multi = Campus(nome='Multi', sigla_campus='MULTI')
            db.session.add(multi)
            db.session.commit()
        
        # 2. Map Campuses
        campuses = {c.nome.lower(): c.id for c in Campus.query.all()}
        campuses['multi'] = multi.id
        # Add basic mapping extensions
        campuses.update({
            'apucarana': campuses.get('apucarana'),
            'campo mourão': campuses.get('campo mourão'),
            'cornélio procópio': campuses.get('cornélio procópio'),
            'curitiba': campuses.get('curitiba'),
            'dois vizinhos': campuses.get('dois vizinhos'),
            'francisco beltrão': campuses.get('francisco beltrão'),
            'guarapuava': campuses.get('guarapuava'),
            'londrina': campuses.get('londrina'),
            'medianeira': campuses.get('medianeira'),
            'pato branco': campuses.get('pato branco'),
            'ponta grossa': campuses.get('ponta grossa'),
            'santa helena': campuses.get('santa helena'),
            'toledo': campuses.get('toledo')
        })

        # 3. Process Data
        lines = RAW_DATA.strip().split('\n')
        updated = 0
        created = 0
        skipped = 0
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Split by Tab or multiple spaces
            # Use split('\t') if tabs, else split by multiple spaces regex
            import re
            parts = re.split(r'\t+', line)
            if len(parts) < 4:
                # Try spaces?
                # But names have spaces.
                # Assuming tab separated from copy paste
                pass
            
            # The input block in task looks tab separated or distinct
            # Let's assume tabs for now, fallback to visual split?
            # User block has specific columns.
            
            if len(parts) < 4:
               # Fallback manual clean
               # Codes are unique patterns: \d+P\d
               pass

            # Safe extraction
            curso = parts[0].strip()
            codigo = parts[1].strip().replace('"', '') # Clean quotes
            sigla = parts[2].strip()
            campus_raw = parts[3].strip()
            
            # Resolve Campus
            target_campus_name = normalize_campus(campus_raw)
            if not target_campus_name:
                print(f"Skipping {curso}: Campus unknown '{campus_raw}'")
                skipped += 1
                continue
                
            campus_id = campuses.get(target_campus_name.lower())
            
            if not campus_id:
                 # Try approximate?
                 print(f"Skipping {curso}: Campus ID not found for '{target_campus_name}'")
                 skipped += 1
                 continue

            # UPSERT by Code
            prog = ProgramaAcademico.query.filter_by(codigo_programa=codigo).first()
            if prog:
                # Update
                prog.nome_programa = curso
                prog.sigla_programa = sigla
                prog.campus_id = campus_id
                updated += 1
            else:
                # Insert
                new_prog = ProgramaAcademico(
                    codigo_programa=codigo,
                    nome_programa=curso,
                    sigla_programa=sigla,
                    campus_id=campus_id
                )
                db.session.add(new_prog)
                created += 1
                
        db.session.commit()
        print(f"DONE. Created: {created}, Updated: {updated}, Skipped: {skipped}")

if __name__ == '__main__':
    main()
