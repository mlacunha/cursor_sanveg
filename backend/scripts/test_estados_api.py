from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
resp = client.get('/api/estados')
print('status', resp.status_code)
print('count', len(resp.json()))
print('sample', resp.json()[:5])
