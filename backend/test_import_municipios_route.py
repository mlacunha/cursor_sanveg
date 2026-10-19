from fastapi.testclient import TestClient
from main import app
from app.config.database import SessionLocal
from app.models.user import SecUser
from app.models.estado import Estado
from app.models.municipio import Municipio
from app.utils.security import create_access_token


class DummyResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def test_import_municipios_route_sync(monkeypatch):
    # Prepare DB: create admin user and an estado TT
    db = SessionLocal()
    try:
        # Clean up any previous test artifacts if present
        db.query(Municipio).filter(Municipio.id == 999999).delete()
        db.query(Estado).filter(Estado.id == 99999).delete()
        db.query(SecUser).filter(SecUser.login == "admin_import").delete()
        db.commit()

        admin = SecUser(login="admin_import", pswd="x", active='Y', priv_admin='Y')
        db.add(admin)
        estado = Estado(id=99999, nome="Teste", sigla="TT")
        db.add(estado)
        db.commit()
    finally:
        db.close()

    token = create_access_token({"sub": "admin_import"})
    client = TestClient(app)

    # Patch requests.get used by the import service to avoid network calls
    import app.services.municipios_import as svc

    def fake_get(url, timeout=10):
        # Return a single municipio payload
        data = [{"id": 999999, "nome": "Municipio Teste"}]
        return DummyResp(data)

    monkeypatch.setattr(svc, "requests", type("R", (), {"get": staticmethod(fake_get)}))

    headers = {"Authorization": f"Bearer {token}"}
    # Call sync to get immediate result
    resp = client.post("/api/municipios/import?estado=TT&sync=true", headers=headers)
    assert resp.status_code in (200, 202)
    body = resp.json()
    assert body["status"] == "completed"
    assert body["results"]["TT"] == 1

    # Verify DB has the imported municipio
    db = SessionLocal()
    try:
        m = db.query(Municipio).filter(Municipio.id == 999999).first()
        assert m is not None
        assert m.nome == "Municipio Teste"
    finally:
        db.close()
