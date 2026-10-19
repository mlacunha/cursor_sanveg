from fastapi.testclient import TestClient
from main import app


def test_list_municipios_by_estado():
    client = TestClient(app)
    # Estado PA (sigla PA) has id 15 in our DB
    resp = client.get('/api/municipios?estado_id=15')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_municipios_by_sigla():
    client = TestClient(app)
    resp = client.get('/api/municipios?estado_sigla=PA')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
