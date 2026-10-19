import os
import sys
import requests

# Allow overriding the server base URL via first CLI arg or SERVER_BASE env var
if len(sys.argv) > 1:
    BASE = sys.argv[1]
else:
    BASE = os.getenv("SERVER_BASE", "http://127.0.0.1:8000")
LOGIN = {"email": "admin@admin.com", "pswd": "admin"}

try:
    r = requests.post(f"{BASE}/api/auth/login", json=LOGIN, timeout=10)
except Exception as exc:
    print("Login request failed:", exc)
    sys.exit(2)

print("Login status:", r.status_code)
try:
    data = r.json()
except Exception:
    print("Login response not JSON:", r.text)
    sys.exit(2)

token = data.get("access_token") or data.get("token")
if not token:
    print("No token returned by login. Response JSON:", data)
    sys.exit(2)

headers = {"Authorization": f"Bearer {token}"}

# list programas
try:
    r2 = requests.get(f"{BASE}/api/programas/", headers=headers, timeout=10)
except Exception as exc:
    print("Request to list programas failed:", exc)
    sys.exit(2)

print("GET /api/programas/ status:", r2.status_code)
try:
    progs = r2.json()
except Exception:
    print("Programas response not JSON:", r2.text)
    sys.exit(2)

if not progs:
    print("No programas found in the system.")
    sys.exit(0)

prog_id = progs[0].get("id")
print("Using programa id:", prog_id)

# call hospedeiros endpoint
try:
    url = f"{BASE}/api/programas/{prog_id}/hospedeiros"
    r3 = requests.get(url, headers=headers, timeout=10)
except Exception as exc:
    print("Request to hospedeiros endpoint failed:", exc)
    sys.exit(2)

print(f"GET /api/programas/{prog_id}/hospedeiros status:", r3.status_code)
print("Response (truncated):")
print(r3.text[:1000])
