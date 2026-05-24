
import sqlite3
import os
import csv
import io

# Setup DB path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "gestao_editais_new.db")

CSV_DATA = """Código - PPG,Nome do curso,Sigla,Campus/campi,Nivel,Área de Avaliação - CAPES,Área Básica - CAPES,Ano Inicio,Nota CAPES
40006018179P5,Engenharia Química,PPGEQ,AP,Mestrado Acadêmico,ENGENHARIAS II,ENGENHARIA QUÍMICA,2019,3
40006018183P2,Textil e Moda,PPGTM,AP,Mestrado Acadêmico,Interdisciplinar ,ENGENHARIA/TECNOLOGIA/GESTÃO,2023,A
40006018182P6,Ciência da Computação,PPGCC,CM,Mestrado Acadêmico,CIÊNCIA DA COMPUTAÇÃO,CIÊNCIA DA COMPUTAÇÃO,2021,A
33283010001P5,Ensino de Física - PROFIS (Polo),PROFIS,CM,Mestrado Profissional em Rede,ASTRONOMIA / FÍSICA,FÍSICA,2014,5
40006018170P8,INOVAÇÕES TECNOLÓGICAS,PPGIT,CM,Mestrado Profissional,Interdisciplinar ,ENGENHARIA/TECNOLOGIA/GESTÃO,2016,3
33004013069P2,Regulamentação de Recursos Hídricos (Polo),PROFÁGUA,CM,Mestrado Profissional em Rede,CIÊNCIAS AMBIENTAIS,CIÊNCIAS AMBIENTAIS,2018,4
40006018037P6,BIOINFORMÁTICA,PPGBIOINFO,CP,Mestrado Acadêmico,CIÊNCIAS BIOLÓGICAS I,GENÉTICA,2015,4
40001016175P8,Bioinformática (Associação com UFPR),PPGAB,CP,Doutorado Acadêmico,CIÊNCIAS BIOLÓGICAS I,GENÉTICA,2020,4
40006018012P3,Engenharia Elétrica,PPGEE,CP,Mestrado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,2010,4
40002012171P9,ENGENHARIA ELETRICA (Associação com UEL),PPGAEE,CP,Doutorado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,2016,4
40006018025P8,Informática,PPGI,CP,Mestrado Profissional,CIÊNCIA DA COMPUTAÇÃO,CIÊNCIA DA COMPUTAÇÃO,2013,4
31075010001P2,Matemática em Rede Nacional (Polo),PROFMAT,CP,Mestrado Profissional em Rede,MATEMÁTICA / PROBABILIDADE E ESTATÍSTICA,MATEMÁTICA,2014,5
40006018024P1,Engenharia Mecânica,PPGEM,CP/PG,Mestrado Acadêmico,ENGENHARIAS III,ENGENHARIA MECÂNICA,2012,3
40006018044P2,ADMINISTRAÇÃO,PPGA,CT,Mestrado Acadêmico,"ADMINISTRAÇÃO PÚBLICA E DE EMPRESAS, CIÊNCIAS CONTÁBEIS E TURISMO",ADMINISTRAÇÃO,2016,3
53045009001P3,ADMINISTRAÇÃO PÚBLICA EM REDE NACIONAL (Polo),PROFIAP,CT,Mestrado Profissional em Rede,"ADMINISTRAÇÃO PÚBLICA E DE EMPRESAS, CIÊNCIAS CONTÁBEIS E TURISMO",ADMINISTRAÇÃO PÚBLICA,2016,3
40006018013P0,CIÊNCIA E TECNOLOGIA AMBIENTAL,PPGCTA,CT,Mestrado Acadêmico,CIÊNCIAS AMBIENTAIS,CIÊNCIAS AMBIENTAIS,2012,4
40006018013P0,CIÊNCIA E TECNOLOGIA AMBIENTAL,PPGCTA,CT,Doutorado Acadêmico,CIÊNCIAS AMBIENTAIS,CIÊNCIAS AMBIENTAIS,2023,4
40006018011P7,Computação Aplicada,PPGCA,CT,Mestrado Profissional,CIÊNCIA DA COMPUTAÇÃO,CIÊNCIA DA COMPUTAÇÃO,2010,3
40006018173P7,Educação Física,PPGEF,CT,Mestrado Acadêmico,EDUCAÇÃO FÍSICA,EDUCAÇÃO FÍSICA,2017,3
40006018018P1,Engenharia Biomédica,PPGEB,CT,Mestrado Profissional,ENGENHARIAS IV,ENGENHARIA BIOMÉDICA,2011,4
40006018008P6,ENGENHARIA CIVIL,PPGEC,CT,Mestrado Acadêmico,ENGENHARIAS I,ENGENHARIA CIVIL,2009,5
40006018008P6,ENGENHARIA CIVIL,PPGEC,CT,Doutorado Acadêmico,ENGENHARIAS I,ENGENHARIA CIVIL,2015,5
40006018001P1,ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL,CPGEI,CT,Mestrado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,1988,6
40006018001P1,ENGENHARIA ELÉTRICA E INFORMÁTICA INDUSTRIAL,CPGEI,CT,Doutorado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,1999,6
40006018003P4,ENGENHARIA MECÂNICA E DE MATERIAIS,PPGEM,CT,Mestrado Acadêmico,ENGENHARIAS III,ENGENHARIA MECÂNICA,2000,4
40006018003P4,ENGENHARIA MECÂNICA E DE MATERIAIS,PPGEM,CT,Doutorado Acadêmico,ENGENHARIAS III,ENGENHARIA MECÂNICA,2012,4
40006018035P3,ESTUDOS DE LINGUAGENS,PPGEL,CT,Mestrado Acadêmico,LINGUíSTICA E LITERATURA,LETRAS,2015,4
40006018172P0,FÍSICA E ASTRONOMIA,PPGFA,CT,Mestrado Acadêmico,ASTRONOMIA / FÍSICA,FÍSICA,2016,3
40006018019P8,"Formação Científica, Educacional e Tecnológica",PPGFCET,CT,Mestrado Profissional,ENSINO,ENSINO DE CIÊNCIAS E MATEMÁTICA,2011,4
40006018019P8,"Formação Científica, Educacional e Tecnológica",PPGFCET,CT,Doutorado Profissional,ENSINO,ENSINO DE CIÊNCIAS E MATEMÁTICA,2019,4
31075010001P2,Matemática em Rede Nacional (Polo),PROFMAT,CT,Mestrado Profissional em Rede,MATEMÁTICA / PROBABILIDADE E ESTATÍSTICA,MATEMÁTICA,2011,5
40006018017P5,Planejamento e Governança Pública,PPGPGP,CT,Mestrado Profissional,PLANEJAMENTO URBANO E REGIONAL / DEMOGRAFIA,PLANEJAMENTO URBANO E REGIONAL,2011,4
40006018017P5,Planejamento e Governança Pública,PPGPGP,CT,Doutorado Profissional,PLANEJAMENTO URBANO E REGIONAL / DEMOGRAFIA,PLANEJAMENTO URBANO E REGIONAL,2019,4
40006018032P4,Química,PPGQ,CT,Mestrado Acadêmico,QUÍMICA,QUÍMICA,2014,3
40006018038P2,SISTEMAS DE ENERGIA,PPGSE,CT,Mestrado Profissional,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,2015,4
40006018181P0,Sustentabilidade Ambiental Urbana,PPGSAU,CT,Doutorado Acadêmico,CIÊNCIAS AMBIENTAIS,CIÊNCIAS AMBIENTAIS,2019,4
40006018002P8,TECNOLOGIA E SOCIEDADE,PPGTE,CT,Mestrado Acadêmico,Interdisciplinar ,SOCIAIS E HUMANIDADES,1995,5
40006018002P8,TECNOLOGIA E SOCIEDADE,PPGTE,CT,Doutorado Acadêmico,Interdisciplinar ,SOCIAIS E HUMANIDADES,2008,5
40006018184P9,Design Prospectivo,PPGDP,CT,Mestrado Acadêmico,"Arquitetura, Urbanismo e e Design",,2025,A
40006018185P5,Educação Tecnológica,PPGET,CT,Mestrado Acadêmico,Educação,,2025,A
40015017009P8,Zootecnia (Associação Unioeste),PPGZO,DV,Mestrado Acadêmico,ZOOTECNIA / RECURSOS PESQUEIROS,ZOOTECNIA,2011,4
40015017009P8,Zootecnia (Associação Unioeste),PPGZO,DV,Doutorado Acadêmico,ZOOTECNIA / RECURSOS PESQUEIROS,ZOOTECNIA,2021,4
40006018043P6,AGROECOSSISTEMAS,PPGSIS,DV/SH,Mestrado Acadêmico,CIÊNCIAS AGRÁRIAS I,AGRONOMIA,2015,3
40006018174P3,Engenharia Ambiental: Análise e Tecnologia Ambiental,PPGEA,FB,Mestrado Acadêmico,ENGENHARIAS I,ENGENHARIA SANITÁRIA,2017,3
40006018175P0,CIÊNCIA E ENGENHARIA DE MATERIAIS,PPGCEM,LD/AP,Mestrado Acadêmico,MATERIAIS,MATERIAIS,2016,4
40006018023P5,Engenharia Ambiental,PPGEA,LD/AP,Mestrado Acadêmico,ENGENHARIAS I,ENGENHARIA SANITÁRIA,2012,4
40006018027P0,"Ensino de Ciências Humanas, Sociais e da Natureza",PPGEN,LD/CP,Mestrado Profissional,ENSINO,ENSINO,2013,4
40006018041P3,ENSINO DE MATEMÁTICA,PPGMAT,LD/CP,Mestrado Profissional,ENSINO,ENSINO DE CIÊNCIAS E MATEMÁTICA,2015,4
40006018015P2,Tecnologia de Alimentos,PPGTAL,LD/FB,Mestrado Profissional,CIÊNCIA DE ALIMENTOS,TECNOLOGIA DE ALIMENTOS,2011,4
33283010001P5,Ensino de Física - PROFIS (Polo),PROFIS,MD,Mestrado Profissional em Rede,ASTRONOMIA / FÍSICA,FÍSICA,2015,5
31102000001P6,PROPRIEDADE INTELECTUAL E TRANSFERÊNCIA DE TECNOLOGIA PARA INOVAÇÃO,PROFNIT,MD,Mestrado Profissional em Rede,"ADMINISTRAÇÃO PÚBLICA E DE EMPRESAS, CIÊNCIAS CONTÁBEIS E TURISMO",ADMINISTRAÇÃO,2023,4
31001017169P2,Química em Rede Nacional (Polo),PROFQUI,MD,Mestrado Profissional em Rede,QUÍMICA,QUÍMICA,2016,4
40006018026P4,Tecnologias Ambientais,PPGTAMB,MD,Mestrado Acadêmico,ENGENHARIAS I,ENGENHARIA SANITÁRIA,2013,4
40006018034P7,TECNOLOGIAS COMPUTACIONAIS PARA O AGRONEGÓCIO,PPGTCA,MD,Mestrado Profissional,Interdisciplinar ,ENGENHARIA/TECNOLOGIA/GESTÃO,2015,4
40006018016P9,Tecnologia de Alimentos,PPGTA,MD/CM,Mestrado Acadêmico,CIÊNCIA DE ALIMENTOS,TECNOLOGIA DE ALIMENTOS,2011,4
40006018016P9,Tecnologia de Alimentos,PPGTA,MD/CM,Doutorado Acadêmico,CIÊNCIA DE ALIMENTOS,TECNOLOGIA DE ALIMENTOS,2023,4
40006018005P7,AGRONOMIA,PPGAG,PB,Mestrado Acadêmico,CIÊNCIAS AGRÁRIAS I,FITOTECNIA,2007,4
40006018005P7,AGRONOMIA,PPGAG,PB,Doutorado Acadêmico,CIÊNCIAS AGRÁRIAS I,FITOTECNIA,2012,4
40006018010P0,Desenvolvimento Regional,PPGDR,PB,Mestrado Acadêmico,PLANEJAMENTO URBANO E REGIONAL / DEMOGRAFIA,PLANEJAMENTO URBANO E REGIONAL,2010,5
40006018010P0,Desenvolvimento Regional,PPGDR,PB,Doutorado Acadêmico,PLANEJAMENTO URBANO E REGIONAL / DEMOGRAFIA,PLANEJAMENTO URBANO E REGIONAL,2019,5
40006018030P1,Engenharia Civil,PPGEC,PB,Mestrado Acadêmico,ENGENHARIAS I,ENGENHARIA CIVIL,2014,3
40006018031P8,Engenharia de Produção e Sistemas,PPGEPS,PB,Mestrado Acadêmico,ENGENHARIAS III,ENGENHARIA DE PRODUÇÃO,2014,3
40006018009P2,ENGENHARIA ELÉTRICA E DE COMPUTAÇÃO,PPGEE,PB,Mestrado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,2009,3
40006018036P0,LETRAS,PPGL,PB,Mestrado Acadêmico,LINGUíSTICA E LITERATURA,LETRAS,2015,4
31075010001P2,Matemática em Rede Nacional (Polo),PROFMAT,PB,Mestrado Profissional em Rede,MATEMÁTICA / PROBABILIDADE E ESTATÍSTICA,MATEMÁTICA,2012,5
40006018020P6,Tecnologia de Processos Químicos e Bioquímicos,PPGTP,PB,Mestrado Acadêmico,ENGENHARIAS II,ENGENHARIA QUÍMICA,2011,3
40006018171P4,CIÊNCIA DA COMPUTAÇÃO,PPGCC,PG,Mestrado Acadêmico,CIÊNCIA DA COMPUTAÇÃO,CIÊNCIA DA COMPUTAÇÃO,2016,3
40006018004P0,ENGENHARIA DE PRODUÇÃO,PPGEP,PG,Mestrado Acadêmico,ENGENHARIAS III,ENGENHARIA DE PRODUÇÃO,2004,5
40006018004P0,ENGENHARIA DE PRODUÇÃO,PPGEP,PG,Doutorado Acadêmico,ENGENHARIAS III,ENGENHARIA DE PRODUÇÃO,2012,5
40006018022P9,Engenharia Elétrica,PPGEE,PG,Mestrado Acadêmico,ENGENHARIAS IV,ENGENHARIA ELÉTRICA,2012,4
40006018177P2,ENGENHARIA QUÍMICA,PPGEQ,PG,Mestrado Acadêmico,ENGENHARIAS II,ENGENHARIA QUÍMICA,2017,3
40006018006P3,ENSINO DE CIÊNCIA E TECNOLOGIA,PPGECT,PG,Mestrado Profissional,ENSINO,ENSINO,2008,5
40006018028P7,ENSINO DE CIÊNCIA E TECNOLOGIA,PPGECT,PG,Doutorado Acadêmico,ENSINO,ENSINO,2013,5
40006018176P6,BIOTECNOLOGIA,PPGBIOTEC,PG/DV,Mestrado Acadêmico,BIOTECNOLOGIA,BIOTECNOLOGIA,2017,4
40006018176P6,BIOTECNOLOGIA,PPGBIOTEC,PG/DV,Doutorado Acadêmico,BIOTECNOLOGIA,BIOTECNOLOGIA,2023,4
40006018178P9,Recursos Naturais e Sustentabilidade,PPGRNS,SH,Mestrado Acadêmico,CIÊNCIAS AMBIENTAIS,CIÊNCIAS AMBIENTAIS,2019,3
31075010001P2,Matemática em Rede Nacional (Polo),PROFMAT,TD,Mestrado Profissional em Rede,MATEMÁTICA / PROBABILIDADE E ESTATÍSTICA,MATEMÁTICA,2018,5
40006018033P0,PROCESSOS QUÍMICOS E BIOTECNOLÓGICOS,PPGQB,TD,Mestrado Acadêmico,ENGENHARIAS II,ENGENHARIA QUÍMICA,2015,3
40006018180P3,Tecnologia Biociências,PPGBIO,TD,Mestrado Profissional,Interdisciplinar ,ENGENHARIA/TECNOLOGIA/GESTÃO,2019,3
"""

def import_csv():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Fetch existing campuses for mapping
    # Assuming sigla_campus is what we use.
    campuses = cursor.execute("SELECT id, sigla_campus FROM campus").fetchall()
    campus_map = {c['sigla_campus']: c['id'] for c in campuses}
    print(f"Loaded {len(campus_map)} campuses.")

    # 2. Parse CSV
    print("Parsing CSV Data...")
    reader = csv.DictReader(io.StringIO(CSV_DATA))
    
    rows_to_process = []
    
    for row in reader:
        # Extract data
        codigo = row['Código - PPG']
        nome = row['Nome do curso']
        sigla = row['Sigla']
        campi_str = row['Campus/campi']
        area_av = row['Área de Avaliação - CAPES']
        area_b = row['Área Básica - CAPES']
        try:
            ano = int(row['Ano Inicio'])
        except:
            ano = None
        nota = row['Nota CAPES']
        
        # Split campuses (Multicampi Logic)
        campi_list = []
        if '/' in campi_str:
            campi_list = campi_str.split('/')
        else:
            campi_list = [campi_str]
            
        for c_sigla in campi_list:
            c_sigla = c_sigla.strip()
            if c_sigla in campus_map:
                cid = campus_map[c_sigla]
                rows_to_process.append({
                    'code': codigo,
                    'name': nome,
                    'sigla': sigla,
                    'campus_id': cid,
                    'area_av': area_av,
                    'area_b': area_b,
                    'year': ano,
                    'nota': nota
                })
            else:
                print(f"WARNING: Campus '{c_sigla}' not found for program {nome}. Skipping link.")

    print(f"Processed {len(rows_to_process)} entries from CSV (expanding multicampi).")
    
    # 3. UPSERT Logic
    # We match by (codigo_programa, campus_id) since code is shared but campus differs.
    # If exists, update metadata. If not, insert.
    
    updates = 0
    inserts = 0
    
    for item in rows_to_process:
        # Check existence
        existing = cursor.execute(
            "SELECT id, ano_inicio FROM programa_academico WHERE codigo_programa = ? AND campus_id = ?",
            (item['code'], item['campus_id'])
        ).fetchone()
        
        if existing:
            # Update
            # For 'ano_inicio', keep the MIN value if multiple rows in CSV have diff years (Mestrado vs Doutorado)
            # But here we process row by row.
            # If DB has Year X, and current row has Year Y. 
            # Logic: Keep the oldest (Foundation year).
            current_db_year = existing['ano_inicio']
            new_year = item['year']
            
            final_year = new_year
            if current_db_year and new_year:
                final_year = min(current_db_year, new_year)
            elif current_db_year:
                final_year = current_db_year
            
            cursor.execute("""
                UPDATE programa_academico
                SET nome_programa = ?, sigla_programa = ?, area_avaliacao = ?, area_basica = ?, ano_inicio = ?, nota_capes = ?
                WHERE id = ?
            """, (item['name'], item['sigla'], item['area_av'], item['area_b'], final_year, item['nota'], existing['id']))
            updates += 1
        else:
            # Insert
            cursor.execute("""
                INSERT INTO programa_academico (codigo_programa, nome_programa, sigla_programa, campus_id, area_avaliacao, area_basica, ano_inicio, nota_capes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item['code'], item['name'], item['sigla'], item['campus_id'], item['area_av'], item['area_b'], item['year'], item['nota']))
            inserts += 1
            
    conn.commit()
    conn.close()
    print(f"Import Complete. Inserts: {inserts}, Updates: {updates}")

if __name__ == "__main__":
    import_csv()
