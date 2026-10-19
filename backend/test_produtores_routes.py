import sys
sys.path.insert(0, 'd:/Projetos/python/FastAPI/api_svegpa')

from main import app

# Obter todas as rotas registradas
routes = []
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        for method in route.methods:
            routes.append(f"{method} {route.path}")

# Filtrar rotas de amostra-coletada
amostra_routes = [r for r in routes if '/api/amostra-coletada' in r]

print("=== ROTAS DE AMOSTRA COLETADA ===")
for route in sorted(amostra_routes):
    print(route)

print(f"\nTotal de rotas de amostra-coletada: {len(amostra_routes)}")
print(f"Total de rotas na aplicação: {len(routes)}")




