"""
Teste de validação de coordenadas com vírgula e ponto
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.relatorio_mapa import RelatorioMapaCSVRow
from decimal import Decimal

print("="*70)
print("TESTE: Coordenadas com vírgula e ponto")
print("="*70)

# Casos de teste
casos = [
    {
        "nome": "Vírgula como separador (padrão brasileiro)",
        "lat": "-3,14159",
        "lon": "-48,5678",
        "esperado_lat": Decimal("-3.14159"),
        "esperado_lon": Decimal("-48.5678")
    },
    {
        "nome": "Ponto como separador (padrão internacional)",
        "lat": "-3.14159",
        "lon": "-48.5678",
        "esperado_lat": Decimal("-3.14159"),
        "esperado_lon": Decimal("-48.5678")
    },
    {
        "nome": "Coordenadas com espaços extras",
        "lat": " -3,14159 ",
        "lon": " -48,5678 ",
        "esperado_lat": Decimal("-3.14159"),
        "esperado_lon": Decimal("-48.5678")
    },
    {
        "nome": "Coordenadas como números (int/float)",
        "lat": -3.14159,
        "lon": -48.5678,
        "esperado_lat": Decimal("-3.14159"),
        "esperado_lon": Decimal("-48.5678")
    },
    {
        "nome": "Coordenadas vazias (devem retornar None)",
        "lat": "",
        "lon": "-",
        "esperado_lat": None,
        "esperado_lon": None
    }
]

for i, caso in enumerate(casos, 1):
    print(f"\nCaso {i}: {caso['nome']}")
    print(f"  Input: lat='{caso['lat']}', lon='{caso['lon']}'")
    
    try:
        # Criar objeto com dados mínimos + coordenadas
        dados = {
            "id_programa": "PROG001",
            "data": "15/01/2024",
            "termo_inspecao": 123,
            "termo_coleta": 456,
            "tipo_imovel": "Rural",
            "municipio": "Belém",
            "cultura": "Açaí",
            "status": "NORMAL",
            "latitude": caso['lat'],
            "longitude": caso['lon']
        }
        
        row = RelatorioMapaCSVRow(**dados)
        
        print(f"  Output: lat={row.latitude}, lon={row.longitude}")
        
        # Validar resultado
        if row.latitude == caso['esperado_lat'] and \
           row.longitude == caso['esperado_lon']:
            print("  Status: ✓ PASSOU")
        else:
            print(f"  Status: ✗ FALHOU")
            print(f"    Esperado: lat={caso['esperado_lat']}, "
                  f"lon={caso['esperado_lon']}")
            
    except Exception as e:
        print(f"  Status: ✗ ERRO - {e}")

print("\n" + "="*70)
print("TESTE CONCLUÍDO")
print("="*70)
