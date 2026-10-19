"""
Script para testar rotas do relatorio_mapa
"""
from main import app

# Filtrar rotas de relatorio-mapa
routes = [
    r for r in app.routes
    if hasattr(r, 'path') and '/api/relatorio-mapa' in str(r.path)
]

print("=== ROTAS DE RELATORIO MAPA ===")
for route in sorted(routes, key=lambda x: str(x.path)):
    methods = ', '.join(route.methods) if hasattr(route, 'methods') else ''
    print(f"{methods} {route.path}")

print(f"\nTotal de rotas de relatorio-mapa: {len(routes)}")

# Contar total de rotas
total_routes = len([r for r in app.routes if hasattr(r, 'path')])
print(f"Total de rotas na aplicação: {total_routes}")
