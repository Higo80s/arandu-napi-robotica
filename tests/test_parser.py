import pytest
from services.parser_strategy import StrictoSensuParser
from utils.formatters import (
    converter_data_br_para_iso, 
    sanitizar_nome, 
    sanitizar_cpf
)

@pytest.fixture
def parser():
    return StrictoSensuParser()

@pytest.fixture
def formulario_exemplo():
    return """
    Cadastramento de bolsa - Stricto Sensu
    Fomento da bolsa: -CAPES - PPG
    Nome completo do bolsista: Valquiria Regina Bressan
    Data de nascimento: 15/08/2002
    CPF (apenas Números) nº: 121.558.099-13
    Nível da bolsa: Mestrado
    Código do Banco: 001
    Agência nº: 2613-1
    Conta Corrente nº: 27223
    Dígito Verificador da Conta Corrente: X
    Data de Início das atividades do bolsista: 09/03/2026
    Tempo concedido: 24
    """

def test_parsing_campos_basicos(parser, formulario_exemplo):
    """Valida se o parser extrai os dados brutos corretamente."""
    resultado = parser.parse(formulario_exemplo)
    
    # O parser já deve devolver sanitizado conforme implementação da Yoko
    assert resultado['nome'] == "VALQUIRIA REGINA BRESSAN"
    assert resultado['cpf'] == "12155809913"
    assert resultado['nivel'] == "Mestrado"
    assert resultado['banco'] == "001"
    assert resultado['nascimento'] == "2002-08-15"

def test_sanitizacao_e_formatacao():
    """Valida se os formatadores convertem os dados para o padrão do banco."""
    nome_sujo = "  Valquiria Regina Bressan  "
    cpf_pontuado = "121.558.099-13"
    data_br = "09/03/2026"
    
    assert sanitizar_nome(nome_sujo) == "VALQUIRIA REGINA BRESSAN"
    assert sanitizar_cpf(cpf_pontuado) == "12155809913"
    assert converter_data_br_para_iso(data_br) == "2026-03-09"

def test_data_invalida_nao_quebra_sistema():
    """Garante que datas malformadas retornem string vazia em vez de Erro 500."""
    assert converter_data_br_para_iso("data_errada") == ""
    assert converter_data_br_para_iso(None) == ""

def test_fallback_campos_vazios(parser):
    """Valida o comportamento do parser com um texto que não contém as chaves esperadas."""
    resultado = parser.parse("Texto aleatório sem chaves de formulário")
    assert resultado == {}
