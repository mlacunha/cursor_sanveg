"""Teste rápido da API do IBGE"""
import requests

url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/PA/municipios"
response = requests.get(url)
municipios = response.json()

# Procurar por Cachoeira
cachoeiras = [m for m in municipios if 'CACHOEIRA' in m['nome'].upper()]
print(f"Municípios com 'CACHOEIRA': {len(cachoeiras)}")
for m in cachoeiras:
    print(f"  - {m['nome']}")
