import os
import sys
import json
from datetime import date, datetime

# Garantir que o script encontre a raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Edital

def json_serial(obj):
    """Fallback para serializar datas em JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def export_rules():
    """Conecta ao banco de dados e exporta editais e regras para JSON estruturado."""
    with app.app_context():
        editais = Edital.query.all()
        data = []
        for e in editais:
            edital_data = {
                "id": e.id,
                "numero": e.numero,
                "descricao": e.descricao,
                "agencia": e.agencia,
                "data_inicio": e.data_inicio,
                "data_fim": e.data_fim,
                "rodadas": [],
                "regras": []
            }
            
            for r in e.rodadas:
                edital_data["rodadas"].append({
                    "id": r.id,
                    "nome": r.nome,
                    "descricao": r.descricao,
                    "data_inicio": r.data_inicio,
                    "data_fim": r.data_fim,
                    "ativa": r.ativa
                })
                
            for regra in e.regras:
                edital_data["regras"].append({
                    "id": regra.id,
                    "descricao": regra.descricao,
                    "ordem": regra.ordem
                })
                
            data.append(edital_data)
            
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'editais_rules.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=json_serial, ensure_ascii=False)
            
        print(f"Sucesso: Exportados {len(data)} editais para {output_file}")

if __name__ == '__main__':
    export_rules()
