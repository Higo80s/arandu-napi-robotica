"""
Gerar lista COMPLETA e DETALHADA dos programas excedentes
Salvar em arquivo para visualização completa
"""

from app import app
from models import ProgramaAcademico, Bolsista
from auditar_programas_sucupira import SUCUPIRA_DATA

with app.app_context():
    programas_db = ProgramaAcademico.query.all()
    db_dict = {p.codigo_programa: p for p in programas_db if p.codigo_programa}
    sucupira_dict = {s['codigo']: s for s in SUCUPIRA_DATA}
    
    # Separar excedentes
    excedentes_grad = []
    excedentes_pos = []
    
    for codigo, prog in db_dict.items():
        if codigo not in sucupira_dict:
            # Contar bolsistas vinculados
            bolsistas_count = Bolsista.query.filter_by(programa_id=prog.id).count()
            
            item = {
                'codigo': codigo,
                'nome': prog.nome_programa,
                'sigla': prog.sigla_programa,
                'campus': prog.campus.sigla_campus if prog.campus else 'N/I',
                'niveis': prog.niveis or 'N/I',
                'nota': prog.nota_capes or 'N/I',
                'bolsistas': bolsistas_count
            }
            
            if prog.niveis == 'GRAD' or 'GRAD-' in codigo:
                excedentes_grad.append(item)
            else:
                excedentes_pos.append(item)
    
    # Salvar em arquivo
    with open('lista_excedentes_completa.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("LISTA COMPLETA DE PROGRAMAS EXCEDENTES\n")
        f.write(f"Banco de Dados vs Plataforma Sucupira\n")
        f.write("=" * 100 + "\n\n")
        
        # Graduação
        f.write(f"1. CURSOS DE GRADUACAO ({len(excedentes_grad)}) - MANTER\n")
        f.write("-" * 100 + "\n")
        f.write("Acao: Manter no banco (nao estao na Sucupira por serem graduacao)\n\n")
        
        for idx, prog in enumerate(excedentes_grad, 1):
            f.write(f"{idx}. Codigo: {prog['codigo']}\n")
            f.write(f"   Nome: {prog['nome']}\n")
            f.write(f"   Sigla: {prog['sigla']} | Campus: {prog['campus']} | Niveis: {prog['niveis']}\n")
            f.write(f"   Bolsistas vinculados: {prog['bolsistas']}\n\n")
        
        # Pós-graduação
        f.write(f"\n2. POS-GRADUACAO NAO ENCONTRADA NA SUCUPIRA ({len(excedentes_pos)})\n")
        f.write("-" * 100 + "\n")
        f.write("Acao Sugerida: Revisar se sao programas descontinuados, duplicatas ou com codigo errado\n\n")
        
        for idx, prog in enumerate(excedentes_pos, 1):
            f.write(f"{idx}. Codigo: {prog['codigo']}\n")
            f.write(f"   Nome: {prog['nome']}\n")
            f.write(f"   Sigla: {prog['sigla']} | Campus: {prog['campus']}\n")
            f.write(f"   Niveis: {prog['niveis']} | Nota CAPES: {prog['nota']}\n")
            f.write(f"   Bolsistas vinculados: {prog['bolsistas']}\n")
            
            # Sugestão baseada em análise
            if prog['bolsistas'] == 0:
                f.write(f"   >>> SUGESTAO: Pode ser EXCLUIDO (sem bolsistas)\n")
            elif 'PPGEM' in prog['sigla'] or 'PPGEA' in prog['sigla']:
                f.write(f"   >>> SUGESTAO: Verificar se e duplicata de programa multicampi\n")
            else:
                f.write(f"   >>> SUGESTAO: Verificar se programa foi descontinuado\n")
            
            f.write("\n")
        
        # Resumo
        f.write("\n" + "=" * 100 + "\n")
        f.write("RESUMO\n")
        f.write("=" * 100 + "\n")
        f.write(f"Total Graduacao: {len(excedentes_grad)} (manter)\n")
        f.write(f"Total Pos-Graduacao: {len(excedentes_pos)} (revisar)\n")
        f.write(f"TOTAL EXCEDENTES: {len(excedentes_grad) + len(excedentes_pos)}\n")
        
        # Análise de bolsistas
        com_bolsistas = sum(1 for p in excedentes_pos if p['bolsistas'] > 0)
        sem_bolsistas = len(excedentes_pos) - com_bolsistas
        
        f.write(f"\nPos-grad COM bolsistas: {com_bolsistas} (manter)\n")
        f.write(f"Pos-grad SEM bolsistas: {sem_bolsistas} (candidatos a exclusao)\n")
        f.write("=" * 100 + "\n")
    
    print(f"\nArquivo gerado: lista_excedentes_completa.txt")
    print(f"Total: {len(excedentes_grad)} graduacao + {len(excedentes_pos)} pos-graduacao = {len(excedentes_grad) + len(excedentes_pos)}")
