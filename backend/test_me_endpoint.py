"""Teste do endpoint /api/auth/me"""
from fastapi.testclient import TestClient
from main import app
from app.utils.security import create_access_token

client = TestClient(app)

# Criar token de teste
token_data = {
    "sub": "admin@admin.com",
    "user_login": "admin"
}
token = create_access_token(token_data)

print(f"Token gerado: {token[:50]}...\n")

# Testar endpoint /me
headers = {"Authorization": f"Bearer {token}"}
response = client.get("/api/auth/me", headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ Endpoint funcionando!")
    print(f"Dados: {response.json()}")
else:
    print("\n❌ Erro no endpoint")
    try:
        print(f"Detalhes: {response.json()}")
    except:
        pass
