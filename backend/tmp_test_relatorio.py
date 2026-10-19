import requests, json
BASE_URL='http://127.0.0.1:8000'
login={'email':'admin@admin.com','pswd':'admin'}
try:
    r=requests.post(BASE_URL+'/api/auth/login', json=login, timeout=10)
    print('login', r.status_code)
    token=r.json().get('access_token')
    print('token len', len(token) if token else None)
    headers={'Authorization':f'Bearer {token}'}
    r=requests.get(BASE_URL+'/api/relatorio-mapa/?limit=5', headers=headers, timeout=10)
    print('list status', r.status_code)
    print(r.text[:1000])
    if r.status_code==200:
        data=r.json()
        if data:
            first=data[0]
            print('first id', first.get('id'))
            r2=requests.get(f"{BASE_URL}/api/relatorio-mapa/{first.get('id')}", headers=headers, timeout=10)
            print('single status', r2.status_code)
            print(r2.text[:1000])
except Exception as e:
    print('error', e)
    import traceback
    traceback.print_exc()
