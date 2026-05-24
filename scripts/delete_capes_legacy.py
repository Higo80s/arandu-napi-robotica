"""
Script para DELETAR registros antigos de 'CAPES' genérica (ID:1)
Esses registros são legados e foram substituídos pelas importações de CAPES PPG e CAPES IES PROPPG
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BolsaVolumetriaAnual, AgenciaFomento
from datetime import datetime

LOG_FILE = f'delete_capes_legacy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

class Logger:
    def __init__(self, filename):
        self.file = open(filename, 'w', encoding='utf-8')
    
    def log(self, msg):
        print(msg)
        self.file.write(msg + '\n')
        self.file.flush()
    
    def close(self):
        self.file.close()

logger = Logger(LOG_FILE)

logger.log("="*80)
logger.log("LIMPEZA DE REGISTROS 'CAPES' GENÉRICA (LEGADOS)")
logger.log("="*80)
logger.log(f"Início: {datetime.now()}")
logger.log("")

with app.app_context():
    try:
        # Buscar agência CAPES genérica (antiga)
        capes_generica = AgenciaFomento.query.filter_by(sigla='CAPES').first()
        
        if not capes_generica:
            logger.log("✓ Agência 'CAPES' genérica não existe mais no banco")
            logger.close()
            exit(0)
        
        logger.log(f"Agência 'CAPES' genérica encontrada (ID: {capes_generica.id})")
        logger.log("")
        
        # Buscar todos os registros com CAPES genérica
        registros_legacy = BolsaVolumetriaAnual.query.filter_by(
            agencia_id=capes_generica.id
        ).all()
        
        logger.log(f"Total de registros com 'CAPES' genérica: {len(registros_legacy)}")
        logger.log("")
        
        if len(registros_legacy) == 0:
            logger.log("✓ Nenhum registro legado encontrado!")
            logger.close()
            exit(0)
        
        # Listar alguns exemplos
        logger.log("Exemplos de registros a deletar:")
        for vol in registros_legacy[:20]:
            logger.log(f"  - {vol.programa.codigo_programa} | {vol.nivel} | {vol.ano_referencia} | qtd={vol.qtd_sistema}")
        
        if len(registros_legacy) > 20:
            logger.log(f"  ... e mais {len(registros_legacy) - 20} registros")
        
        logger.log("")
        logger.log("="*80)
        logger.log("DELETANDO REGISTROS LEGADOS")
        logger.log("="*80)
        logger.log("")
        
        # Deletar todos os registros legados
        deletados = 0
        for vol in registros_legacy:
            db.session.delete(vol)
            deletados += 1
            
            if deletados % 50 == 0:
                logger.log(f"  Deletados: {deletados}/{len(registros_legacy)}")
        
        # Commit
        db.session.commit()
        
        logger.log("")
        logger.log("="*80)
        logger.log("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        logger.log("="*80)
        logger.log(f"Total de registros deletados: {deletados}")
        logger.log(f"Fim: {datetime.now()}")
        logger.log("")
        logger.log("IMPORTANTE:")
        logger.log("  Os registros corretos estão em CAPES PPG e CAPES IES PROPPG")
        logger.log("  Verifique o relatório: http://127.0.0.1:5003/reports/evolution/view")
        logger.log("")
        
    except Exception as e:
        db.session.rollback()
        logger.log("")
        logger.log("="*80)
        logger.log("❌ ERRO DURANTE LIMPEZA!")
        logger.log("="*80)
        logger.log(f"Erro: {e}")
        import traceback
        logger.log(traceback.format_exc())
        logger.log("")
        logger.log("A transação foi revertida (ROLLBACK).")
        logger.log("")
        raise

logger.close()
print(f"\nLog completo salvo em: {LOG_FILE}")
