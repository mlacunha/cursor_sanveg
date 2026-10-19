"""
Script para testar importação de CSV do relatorio_mapa
"""
import requests
import sys

# Configuração
API_URL = "http://localhost:8000"
CSV_FILE_PATH = "seu_arquivo.csv"  # Altere para o caminho do seu CSV

def login():
    """Faz login e retorna o token"""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={
            "username": "seu_usuario",  # Altere para seu usuário
            "password": "sua_senha"      # Altere para sua senha
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Erro no login: {response.status_code}")
        print(response.text)
        sys.exit(1)

def import_csv(token, csv_path):
    """Importa o arquivo CSV"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(csv_path, 'rb') as f:
        files = {'file': (csv_path, f, 'text/csv')}
        response = requests.post(
            f"{API_URL}/api/relatorio-mapa/import-csv",
            headers=headers,
            files=files
        )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

if __name__ == "__main__":
    # Permitir passar o caminho do CSV como argumento
    if len(sys.argv) > 1:
        CSV_FILE_PATH = sys.argv[1]
    
    print(f"Fazendo login...")
    token = login()
    print(f"Token obtido: {token[:20]}...")
    
    print(f"\nImportando CSV: {CSV_FILE_PATH}")
    import_csv(token, CSV_FILE_PATH)
