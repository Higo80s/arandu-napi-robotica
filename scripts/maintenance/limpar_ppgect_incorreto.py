"""
Verifica e limpa código PPGECT incorreto (40006018012p4)
"""

from app import app, db
from models import ProgramaAcademico, Bolsista

with app.app_context():
    print("=== VERIFICANDO CODIGO INCORRETO 40006018012p4 ===\n")
    
    # Buscar programa com código incorreto
    prog_incorreto = ProgramaAcademico.query.filter_by(codigo_programa="40006018012p4").first()
    
    if not prog_incorreto:
        # Tentar outras variações
        prog_incorreto = ProgramaAcademico.query.filter(
            ProgramaAcademico.codigo_programa.ilike("40006018012%")
        ).first()
    
    if prog_incorreto:
        print(f"❌ ENCONTRADO programa com código incorreto!")
        print(f"   ID: {prog_incorreto.id}")
        print(f"   Nome: {prog_incorreto.nome_programa}")
        print(f"   Código: {prog_incorreto.codigo_programa}")
        
        # Verificar bolsistas vinculados
        bolsistas = Bolsista.query.filter_by(programa_id=prog_incorreto.id).all()
        print(f"\n   Bolsistas vinculados: {len(bolsistas)}")
        
        if bolsistas:
            print("\n   Transferindo bolsistas para programas corretos...")
            
            for b in bolsistas:
                nivel = b.modalidade.nivel.upper() if b.modalidade else 'DESCONHECIDO'
                
                if 'MESTRADO' in nivel or 'M' == nivel:
                    # Transferir para Mestrado (ID 42)
                    b.programa_id = 42
                    print(f"   - {b.nome}: transferido para PPGECT Mestrado (ID 42)")
                elif 'DOUTORADO' in nivel or 'D' == nivel:
                    # Transferir para Doutorado (ID 130)
                    b.programa_id = 130
                    print(f"   - {b.nome}: transferido para PPGECT Doutorado (ID 130)")
                else:
                    print(f"   - {b.nome}: NIVEL DESCONHECIDO ({nivel}) - mantido sem alteração")
            
            db.session.commit()
            print("\n   ✅ Bolsistas transferidos!")
        
        # Deletar programa incorreto
        print(f"\n   Removendo programa incorreto (ID {prog_incorreto.id})...")
        db.session.delete(prog_incorreto)
        db.session.commit()
        print("   ✅ Programa removido!")
        
    else:
        print("✅ Nenhum programa com código incorreto encontrado!")
    
    # Verificar programas PPGECT finais
    print("\n=== PPGECT CORRETOS NO SISTEMA ===\n")
    ppgects = ProgramaAcademico.query.filter_by(sigla_programa='PPGECT').order_by(ProgramaAcademico.id).all()
    
    for p in ppgects:
        bolsistas_count = Bolsista.query.filter_by(programa_id=p.id).count()
        print(f"ID {p.id}: {p.codigo_programa}")
        print(f"   {p.nome_programa}")
        print(f"   {bolsistas_count} bolsistas")
        print()
