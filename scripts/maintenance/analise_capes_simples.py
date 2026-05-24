"""
Análise de discrepância - Versão com output em arquivo
"""

from app import app, db
from models import Bolsista, Modalidade, Edital

with app.app_context():
    lines = []
    lines.append("=== COMPARACAO COM DADOS OFICIAIS CAPES ===\n")
    
    # Dados oficiais
    oficial_total = 429
    oficial_m_ppg = 255
    oficial_d_ppg = 151
    oficial_m_ies = 14
    oficial_d_ies = 9
    
    lines.append("DADOS OFICIAIS CAPES:")
    lines.append(f"  Total: {oficial_total}")
    lines.append(f"  Mestrado PPG: {oficial_m_ppg}")
    lines.append(f"  Doutorado PPG: {oficial_d_ppg}")
    lines.append(f"  Mestrado IES: {oficial_m_ies}")
    lines.append(f"  Doutorado IES: {oficial_d_ies}")
    
    # Dados do sistema
    lines.append("\n=== DADOS DO SISTEMA ===\n")
    
    total_ativos = Bolsista.query.filter_by(ativo=True).count()
    lines.append(f"Total bolsistas ATIVOS: {total_ativos}")
    
    # Por nível
    mestrado = Bolsista.query.join(Modalidade).filter(
        Bolsista.ativo==True,
        Modalidade.nivel.ilike('%mestrado%')
    ).count()
    
    doutorado = Bolsista.query.join(Modalidade).filter(
        Bolsista.ativo==True,
        Modalidade.nivel.ilike('%doutorado%')
    ).count()
    
    lines.append(f"  Mestrado: {mestrado}")
    lines.append(f"  Doutorado: {doutorado}")
    
    # Por edital
    lines.append("\n=== POR EDITAL ===\n")
    
    editais = Edital.query.all()
    for edital in editais:
        bolsistas = Bolsista.query.filter_by(edital_id=edital.id, ativo=True).count()
        if bolsistas > 0:
            lines.append(f"{edital.numero[:40]:40s} ({edital.agencia[:10]:10s}): {bolsistas:3d} bolsistas")
    
    # Discrepância
    lines.append("\n=== DISCREPANCIA ===\n")
    
    diff_total = total_ativos - oficial_total
    lines.append(f"Diferenca total: {diff_total:+d}")
    
    if diff_total > 0:
        lines.append(f"\nSistema tem {diff_total} bolsistas A MAIS que o oficial CAPES")
    
    # Salvar
    with open('analise_capes_resultado.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print('\n'.join(lines))
    print("\nArquivo salvo: analise_capes_resultado.txt")
