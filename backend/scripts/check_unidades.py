import requests

BASE = 'http://127.0.0.1:8000'

print('Logging in...')
r = requests.post(BASE + '/api/auth/login', json={'email': 'admin@admin.com', 'pswd': 'admin'}, timeout=10)
print('login status', r.status_code)
if r.status_code != 200:
    print(r.text)
    raise SystemExit(1)

token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

print('Listing orgaos...')
r = requests.get(BASE + '/api/orgaos/', headers=headers, timeout=10)
print('/api/orgaos', r.status_code)
orgs = r.json() if r.status_code == 200 else []
if not orgs:
    print('No orgaos found')
    raise SystemExit(0)

org0 = orgs[0]
org_id = org0.get('id')
print('Using orgao id:', org_id)

print('Calling /api/unidades?id_orgao=...')
r = requests.get(BASE + '/api/unidades', headers=headers, params={'id_orgao': org_id}, timeout=10)
print('/api/unidades filtered', r.status_code)
print(r.text[:2000])
