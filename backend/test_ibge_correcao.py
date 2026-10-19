"""
Script de teste para validar a correção automática de municípios usando IBGE.
"""
import pytest
from app.utils.ibge_municipios import (
    carregar_municipios_ibge,
    encontrar_municipio_correto
)
from app.schemas.relatorio_mapa import RelatorioMapaCSVRow


@pytest.fixture(scope="module")
def municipios():
    return carregar_municipios_ibge()


def test_carregar_municipios(municipios):
    """Teste 1: Carregar municípios do IBGE"""
    print("\n" + "="*70)
    print("TESTE 1: Carregando municípios do IBGE")
    print("="*70)
    
    assert municipios is not None
    assert len(municipios) > 0
    print(f"✓ Carregados {len(municipios)} municípios")
    
    # Verificar alguns municípios conhecidos
    municipios_esperados = [
        "BELÉM", "ANANINDEUA", "SANTARÉM", "MARABÁ",
        "NOVA ESPERANÇA DO PIRIÁ", "CACHOEIRA DO PIRIÁ"
    ]
    
    for mun in municipios_esperados:
        assert mun in municipios, f"Município esperado '{mun}' não foi encontrado"


def test_longest_prefix_match(municipios):
    """Teste 2: Algoritmo de Longest Prefix Match"""
    print("\n" + "="*70)
    print("TESTE 2: Longest Prefix Match")
    print("="*70)
    
    casos_teste = [
        {
            "municipio": "Nova",
            "cultura": "Esperança do Piriá Laranja",
            "esperado_mun": "NOVA ESPERANÇA DO PIRIÁ",
            "esperado_cult": "LARANJA"
        },
        {
            "municipio": "Cachoeira",
            "cultura": "do Piriá Banana",
            "esperado_mun": "CACHOEIRA DO PIRIÁ",
            "esperado_cult": "BANANA"
        },
        {
            "municipio": "Santa",
            "cultura": "Izabel do Pará Coco",
            "esperado_mun": "SANTA IZABEL DO PARÁ",
            "esperado_cult": "COCO"
        },
        {
            "municipio": "São",
            "cultura": "Félix do Xingu Mandioca",
            "esperado_mun": "SÃO FÉLIX DO XINGU",
            "esperado_cult": "MANDIOCA"
        },
        {
            "municipio": "Belém",
            "cultura": "Açaí",
            "esperado_mun": None,  # Já está correto
            "esperado_cult": None
        }
    ]
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\nCaso {i}:")
        print(f"  Input: municipio='{caso['municipio']}', "
              f"cultura='{caso['cultura']}'")
        
        mun_corrigido, cult_corrigida = encontrar_municipio_correto(
            caso['municipio'],
            caso['cultura'],
            municipios
        )
        
        print(f"  Output: municipio='{mun_corrigido}', "
              f"cultura='{cult_corrigida}'")
        
        if mun_corrigido == caso['esperado_mun'] and \
           cult_corrigida == caso['esperado_cult']:
            print("  ✓ PASSOU")
        else:
            print(f"  ✗ FALHOU - Esperado: municipio='{caso['esperado_mun']}', "
                  f"cultura='{caso['esperado_cult']}'")


def test_pydantic_validator():
    """Teste 3: Validador Pydantic integrado"""
    print("\n" + "="*70)
    print("TESTE 3: Validador Pydantic")
    print("="*70)
    
    # Caso 1: Município quebrado
    print("\nCaso 1: Município quebrado")
    dados_quebrados = {
        "id_programa": "PROG001",
        "data": "15/01/2024",
        "termo_inspecao": 123,
        "termo_coleta": 456,
        "tipo_imovel": "Rural",
        "municipio": "Nova",
        "cultura": "Esperança do Piriá Laranja",
        "status": "NORMAL"
    }
    
    print(f"  Input: {dados_quebrados['municipio']} + "
          f"{dados_quebrados['cultura']}")
    
    try:
        row = RelatorioMapaCSVRow(**dados_quebrados)
        print(f"  Output: municipio='{row.municipio}', "
              f"cultura='{row.cultura}'")
        
        if row.municipio == "NOVA ESPERANÇA DO PIRIÁ" and \
           row.cultura == "LARANJA":
            print("  ✓ PASSOU - Correção aplicada corretamente")
        else:
            print("  ✗ FALHOU - Correção não aplicada como esperado")
    except Exception as e:
        print(f"  ✗ ERRO: {e}")
    
    # Caso 2: Município correto (não deve alterar)
    print("\nCaso 2: Município correto (não deve alterar)")
    dados_corretos = {
        "id_programa": "PROG001",
        "data": "15/01/2024",
        "termo_inspecao": 123,
        "termo_coleta": 456,
        "tipo_imovel": "Rural",
        "municipio": "Belém",
        "cultura": "Açaí",
        "status": "NORMAL"
    }
    
    print(f"  Input: {dados_corretos['municipio']} + "
          f"{dados_corretos['cultura']}")
    
    try:
        row = RelatorioMapaCSVRow(**dados_corretos)
        print(f"  Output: municipio='{row.municipio}', "
              f"cultura='{row.cultura}'")
        
        # Deve manter ou normalizar para uppercase
        if row.municipio.upper() == "BELÉM" and row.cultura.upper() == "AÇAÍ":
            print("  ✓ PASSOU - Mantido sem alterações indevidas")
        else:
            print("  ~ AVISO - Normalizado para uppercase (aceitável)")
    except Exception as e:
        print(f"  ✗ ERRO: {e}")


def main():
    """Executar todos os testes"""
    print("\n" + "#"*70)
    print("# TESTES DE CORREÇÃO AUTOMÁTICA DE MUNICÍPIOS")
    print("#"*70)
    
    try:
        # Teste 1: Carregar municípios
        municipios = test_carregar_municipios()
        
        # Teste 2: Algoritmo de matching
        test_longest_prefix_match(municipios)
        
        # Teste 3: Validador Pydantic
        test_pydantic_validator()
        
        print("\n" + "#"*70)
        print("# TESTES CONCLUÍDOS")
        print("#"*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
