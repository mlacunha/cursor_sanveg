"""Teste simples e direto do endpoint /me"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Login
print("Fazendo login...")
response = client.post("/api/auth/login", json={
    "email": "admin@admin.com",
    "pswd": "admin"
})

if response.status_code != 200:
    print(f"Erro no login: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"Token obtido: {token[:50]}...\n")

# Testar /me
print("Testando /api/auth/me...")
try:
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Sucesso!")
        print(f"Dados: {response.json()}")
    else:
        print(f"❌ Erro!")
        print(f"Resposta: {response.text}")
except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()
