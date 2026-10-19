"""Teste rápido do fluxo de autenticação com a nova tabela users."""
import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

# 1. Login
payload = json.dumps({"email": "admin@sanveg.com", "password": "Admin@2025"}).encode()
req = urllib.request.Request(
    BASE + "/api/auth/login",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = urllib.request.urlopen(req)
data = json.loads(res.read())
token = data["access_token"]
user = data["user"]

print("[OK] Login bem-sucedido!")
print(f"     login  : {user['login']}")
print(f"     nome   : {user['nome']}")
print(f"     role   : {user['role']}")
print(f"     token  : {token[:40]}...")

# 2. /me
req2 = urllib.request.Request(
    BASE + "/api/auth/me",
    headers={"Authorization": f"Bearer {token}"},
)
res2 = urllib.request.urlopen(req2)
me = json.loads(res2.read())
print()
print("[OK] /api/auth/me respondeu corretamente:")
print(f"     id     : {me['id']}")
print(f"     email  : {me['email']}")
print(f"     active : {me['active']}")
print(f"     role   : {me['role']}")

# 3. GET /api/users/ (rota de admin)
req3 = urllib.request.Request(
    BASE + "/api/users/",
    headers={"Authorization": f"Bearer {token}"},
)
res3 = urllib.request.urlopen(req3)
users_list = json.loads(res3.read())
print()
print(f"[OK] GET /api/users/ retornou {len(users_list)} usuario(s)")
for u in users_list:
    print(f"     - {u['login']} | {u['role']} | active={u['active']}")
