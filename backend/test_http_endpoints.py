"""Teste real dos endpoints via HTTP"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

if __name__ == '__main__':
    print("=== TESTE REAL DOS ENDPOINTS ===\n")

    # 1. Login
    print("1. Testando POST /api/auth/login...")
    login_data = {
        "email": "admin@admin.com",
        "pswd": "admin"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login bem-sucedido!")
            print(f"   Token: {data['access_token'][:50]}...")
            print(f"   User: {data['user']['login']}")
            token = data['access_token']
        else:
            print(f"   ❌ Erro no login: {response.text}")
            exit(1)
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        exit(1)

    # 2. Testar /me
    print("\n2. Testando GET /api/auth/me...")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint /me funcionando!")
            print(f"   Dados retornados:")
            print(f"   {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
            # Tentar ver o erro detalhado
            try:
                error_detail = response.json()
                print(f"   Detalhes do erro: {json.dumps(error_detail, indent=2)}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== FIM DOS TESTES ===")
