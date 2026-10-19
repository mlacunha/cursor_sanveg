import os
import sys
import requests

# Allow overriding the server base URL via first CLI arg or SERVER_BASE env var
if len(sys.argv) > 1:
    BASE = sys.argv[1]
else:
    BASE = os.getenv('SERVER_BASE', 'http://127.0.0.1:8000')

LOGIN = {'email': 'admin@admin.com', 'pswd': 'admin'}

try:
    r = requests.post(f"{BASE}/api/auth/login", json=LOGIN, timeout=10)
except Exception as exc:
    print('Login request failed:', exc)
    sys.exit(2)

print('Login status:', r.status_code)
try:
    data = r.json()
except Exception:
    print('Login response not JSON:', r.text)
    sys.exit(2)

token = data.get('access_token') or data.get('token')
if not token:
    print('No token returned by login. Response JSON:', data)
    sys.exit(2)

headers = {'Authorization': f'Bearer {token}'}

# list normas (no filters)
try:
    r2 = requests.get(f"{BASE}/api/normas/", headers=headers, timeout=10)
except Exception as exc:
    print('Request to list normas failed:', exc)
    sys.exit(2)

print('GET /api/normas/ status:', r2.status_code)
try:
    normas = r2.json()
except Exception:
    print('Normas response not JSON:', r2.text)
    sys.exit(2)

if not normas:
    print('No normas found in the system.')
    sys.exit(0)

# pick first norma to extract id_programa and nome_norma fragment
norma0 = normas[0]
prog_id = norma0.get('id_programa')
nome = norma0.get('nome_norma')
print('Using programa id:', prog_id)
print('Using nome_norma sample:', nome)

# call normas endpoint with filters
params = {'id_programa': prog_id, 'nome_norma': nome.split()[0]}
try:
    r3 = requests.get(
        f"{BASE}/api/normas/",
        headers=headers,
        params=params,
        timeout=10
    )
except Exception as exc:
    print('Request to normas endpoint failed:', exc)
    sys.exit(2)

print('GET /api/normas with filters status:', r3.status_code)
print('Response (truncated):')
print(r3.text[:1000])
