"""Teste dos endpoints de sync: push e pull."""
import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

# 1. Login para obter token
payload = json.dumps({"email": "admin@sanveg.com", "password": "Admin@2025"}).encode()
req = urllib.request.Request(
    BASE + "/api/auth/login",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = urllib.request.urlopen(req)
token = json.loads(res.read())["access_token"]
auth = {"Authorization": f"Bearer {token}"}
print(f"[OK] Token obtido: {token[:30]}...")

# 2. Teste GET /api/sync/pull
req_pull = urllib.request.Request(BASE + "/api/sync/pull", headers=auth)
res_pull = urllib.request.urlopen(req_pull)
pull_data = json.loads(res_pull.read())
print()
print("[OK] GET /api/sync/pull respondeu:")
for key, val in pull_data.items():
    print(f"     {key:20s}: {len(val)} registros")

# 3. Teste POST /api/sync/push (fila vazia)
push_payload = json.dumps({"queue": []}).encode()
req_push = urllib.request.Request(
    BASE + "/api/sync/push",
    data=push_payload,
    headers={**auth, "Content-Type": "application/json"},
    method="POST",
)
res_push = urllib.request.urlopen(req_push)
push_result = json.loads(res_push.read())
print()
print("[OK] POST /api/sync/push (fila vazia):")
print(f"     processed_ids : {push_result['processed_ids']}")
print(f"     errors        : {push_result['errors']}")
