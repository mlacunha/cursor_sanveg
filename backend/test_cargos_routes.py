"""Test script to verify cargos routes are registered"""
from main import app

print("=== All registered routes ===\n")

routes_by_tag = {}

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
        tag = route.tags[0] if hasattr(route, 'tags') and route.tags else "No tag"
        
        if tag not in routes_by_tag:
            routes_by_tag[tag] = []
        
        routes_by_tag[tag].append(f"{methods:6} {route.path}")

for tag, routes in sorted(routes_by_tag.items()):
    print(f"\n[{tag}]")
    for route in sorted(routes):
        print(f"  {route}")

print("\n=== Total routes by tag ===")
for tag, routes in sorted(routes_by_tag.items()):
    print(f"{tag}: {len(routes)} routes")
