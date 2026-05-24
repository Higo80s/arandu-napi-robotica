"""
Script para verificar e criar agências CAPES no banco
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import AgenciaFomento

with app.app_context():
    print("="*80)
    print("AGÊNCIAS NO BANCO")
    print("="*80)
    
    agencias = AgenciaFomento.query.all()
    for ag in agencias:
        print(f"  - {ag.sigla} (ID: {ag.id})")
    
    print("\n" + "="*80)
    print("VERIFICANDO AGÊNCIAS CAPES")
    print("="*80)
    
    # Verificar se existem as duas agências CAPES
    capes_ppg = AgenciaFomento.query.filter_by(sigla='CAPES PPG').first()
    capes_ies = AgenciaFomento.query.filter_by(sigla='CAPES IES PROPPG').first()
    
    if capes_ppg:
        print(f"✓ CAPES PPG já existe (ID: {capes_ppg.id})")
    else:
        print("✗ CAPES PPG não existe - precisa criar")
    
    if capes_ies:
        print(f"✓ CAPES IES PROPPG já existe (ID: {capes_ies.id})")
    else:
        print("✗ CAPES IES PROPPG não existe - precisa criar")
    
    print("\n" + "="*80)
    print("CRIAR AGÊNCIAS? (se necessário)")
    print("="*80)
    
    criadas = []
    
    if not capes_ppg:
        nova = AgenciaFomento(sigla='CAPES PPG', nome='CAPES - Programa de Pós-Graduação')
        db.session.add(nova)
        criadas.append('CAPES PPG')
        print("+ Criando CAPES PPG...")
    
    if not capes_ies:
        nova = AgenciaFomento(sigla='CAPES IES PROPPG', nome='CAPES - IES PROPPG')
        db.session.add(nova)
        criadas.append('CAPES IES PROPPG')
        print("+ Criando CAPES IES PROPPG...")
    
    if criadas:
        db.session.commit()
        print(f"\n✓ Agências criadas: {', '.join(criadas)}")
    else:
        print("\n✓ Todas as agências já existem")
    
    print("\n" + "="*80)
    print("AGÊNCIAS FINAIS NO BANCO")
    print("="*80)
    
    agencias = AgenciaFomento.query.all()
    for ag in agencias:
        print(f"  - {ag.sigla} (ID: {ag.id})")
