"""
Teste simples e direto da correção de municípios
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("TESTE 1: Carregando municípios do IBGE")
print("="*70)

from app.utils.ibge_municipios import carregar_municipios_ibge, encontrar_municipio_correto

municipios = carregar_municipios_ibge()
print(f"✓ Carregados {len(municipios)} municípios\n")

print("="*70)
print("TESTE 2: Testando correção de municípios quebrados")
print("="*70)

# Caso 1: Nova Esperança do Piriá (deve retornar grafia original IBGE)
print("\nCaso 1: Nova + Esperança do Piriá Laranja")
mun, cult = encontrar_municipio_correto("Nova", "Esperança do Piriá Laranja")
print(f"  Município corrigido: {mun}")
print(f"  Cultura corrigida: {cult}")
esperado_mun = 'Nova Esperança do Piriá'  # Title Case (grafia IBGE)
esperado_cult = 'Laranja'
if mun == esperado_mun and cult == esperado_cult:
    print(f"  Status: ✓ PASSOU (grafia original IBGE preservada)")
else:
    print(f"  Status: ✗ FALHOU - Esperado '{esperado_mun}' / '{esperado_cult}'")

# Caso 2: Cachoeira do Piriá (deve retornar grafia original IBGE)
print("\nCaso 2: Cachoeira + do Piriá Banana")
mun, cult = encontrar_municipio_correto("Cachoeira", "do Piriá Banana")
print(f"  Município corrigido: {mun}")
print(f"  Cultura corrigida: {cult}")
esperado_mun2 = 'Cachoeira do Piriá'  # Title Case (grafia IBGE)
esperado_cult2 = 'Banana'
if mun == esperado_mun2 and cult == esperado_cult2:
    print(f"  Status: ✓ PASSOU (grafia original IBGE preservada)")
else:
    print(f"  Status: ✗ FALHOU - Esperado '{esperado_mun2}' / '{esperado_cult2}'")

# Caso 3: Belém (já correto)
print("\nCaso 3: Belém + Açaí (já correto, não deve alterar)")
mun, cult = encontrar_municipio_correto("Belém", "Açaí")
print(f"  Município: {mun}")
print(f"  Cultura: {cult}")
print(f"  Status: {'✓ PASSOU' if mun is None else '✗ Alterou indevidamente'}")

print("\n" + "="*70)
print("TESTE 3: Validador Pydantic completo")
print("="*70)

from app.schemas.relatorio_mapa import RelatorioMapaCSVRow

dados_teste = {
    "id_programa": "PROG001",
    "data": "15/01/2024",
    "termo_inspecao": 123,
    "termo_coleta": 456,
    "tipo_imovel": "Rural",
    "municipio": "Nova",
    "cultura": "Esperança do Piriá Laranja",
    "status": "NORMAL"
}

print(f"\nInput: municipio='{dados_teste['municipio']}', cultura='{dados_teste['cultura']}'")

row = RelatorioMapaCSVRow(**dados_teste)

print(f"Output: municipio='{row.municipio}', cultura='{row.cultura}'")
esperado_mun = "Nova Esperança do Piriá"  # Grafia original IBGE
esperado_cult = "Laranja"
if row.municipio == esperado_mun and row.cultura == esperado_cult:
    print("✓ PASSOU - Validador com grafia IBGE original!")
else:
    print(f"✗ FALHOU - Esperado: {esperado_mun} / {esperado_cult}")

print("\n" + "="*70)
print("TODOS OS TESTES CONCLUÍDOS!")
print("="*70)
