import re
from utils.formatters import (
    converter_data_br_para_iso, 
    sanitizar_nome, 
    sanitizar_cpf,
    formatar_agencia_conta
)

class StrictoSensuParser:
    """Strategy para processar formulários de Cadastramento Stricto Sensu."""
    
    def parse(self, text):
        if not text:
            return {}
            
        # 0. PRÉ-PROCESSAMENTO (Yoko's Touch: Zero-Gravity)
        # Remove todos os parênteses e seus conteúdos (ex: "(não informar dígito verificador)")
        # Isso evita que as quebras de linha dentro dos parênteses quebrem as regex principais.
        clean_text = re.sub(r'\(.*?\)', '', text, flags=re.DOTALL).replace('\r', '')
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        raw_data = {}
        
        def find_value_after(keyword):
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    # Tenta pegar na mesma linha se houver " : valor"
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        val = parts[1].strip()
                        if re.search(r'[a-zA-Z0-9]', val):
                            return val
                    # Caso contrário, procura nas próximas 3 linhas válidas
                    for j in range(i + 1, min(i + 4, len(lines))):
                        val = lines[j].strip()
                        if re.search(r'[a-zA-Z0-9]', val):
                            # Tira ":" do começo se sobrou da quebra
                            return val.lstrip(':').strip()
            return None

        raw_data['nome'] = find_value_after('nome completo')
        raw_data['cpf'] = find_value_after('cpf')
        raw_data['nascimento'] = find_value_after('data de nascimento')
        raw_data['nivel'] = find_value_after('nível da bolsa')
        raw_data['banco'] = find_value_after('código do banco')
        raw_data['agencia'] = find_value_after('agência')
        raw_data['conta'] = find_value_after('conta corrente')
        raw_data['dv'] = find_value_after('dígito verificador')
        
        raw_data['ingresso'] = find_value_after('data de ingresso')
        raw_data['inicio_atividades'] = find_value_after('início das atividades')
        raw_data['meses_concedidos'] = find_value_after('tempo concedido')
        
        raw_data['fomento'] = find_value_after('fomento da bolsa')
        raw_data['programa'] = find_value_after('nome do programa')
        raw_data['campus'] = find_value_after('campus')
        raw_data['codigo_programa'] = find_value_after('código do programa')
        raw_data['previsao_defesa'] = find_value_after('previsão de defesa')

        data = {}
        # Sanitização e Formatação Integrada (Yoko's Touch)
        if any(raw_data.values()):
            data = {
                'nome': sanitizar_nome(raw_data.get('nome')),
                'cpf': sanitizar_cpf(raw_data.get('cpf')),
                'nascimento': converter_data_br_para_iso(raw_data.get('nascimento')),
                'nivel': raw_data.get('nivel'),
                'banco': raw_data.get('banco'),
                'agencia': formatar_agencia_conta(raw_data.get('agencia')),
                'conta': formatar_agencia_conta(raw_data.get('conta')),
                'dv': formatar_agencia_conta(raw_data.get('dv')),
                'ingresso': converter_data_br_para_iso(raw_data.get('ingresso')),
                'inicio_atividades': converter_data_br_para_iso(raw_data.get('inicio_atividades')),
                'meses': re.search(r'\d+', raw_data.get('meses_concedidos') or '').group(0) if raw_data.get('meses_concedidos') else None,
                'fomento': raw_data.get('fomento'),
                'programa': raw_data.get('programa'),
                'campus': raw_data.get('campus'),
                'codigo_programa': raw_data.get('codigo_programa'),
                'previsao_defesa': converter_data_br_para_iso(raw_data.get('previsao_defesa'))
            }

        return data
