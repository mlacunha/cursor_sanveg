from main import app

print("✅ App carregado com sucesso")

routes = [r for r in app.routes if hasattr(r, 'path') and '/orgaos' in r.path]
print(f"\nRotas de órgãos: {len(routes)}")
for r in routes:
    methods = r.methods if hasattr(r, 'methods') else {'GET'}
    print(f"  {list(methods)} {r.path}")
