from fastapi.testclient import TestClient
from main import app
from app.config.database import SessionLocal
from app.models.user import SecUser
from app.models.produtor import Produtor
from app.models.estado import Estado
from app.models.municipio import Municipio
from app.utils.security import create_access_token
import uuid


def test_produtor_get_includes_location_info():
    db = SessionLocal()
    try:
        # find an existing estado to attach to test municipio
        estado = db.query(Estado).filter(Estado.sigla == 'PA').first()
        if not estado:
            # fallback: use any estado
            estado = db.query(Estado).first()

        # Try to find an existing municipio in the chosen estado to avoid inserting
        m = db.query(Municipio).filter(Municipio.estado_id == estado.id).first()
        if m:
            unique_name = m.nome
            created_municipio = False
        else:
            # fallback: if none exists, use any existing municipio or mark for creation
            m_any = db.query(Municipio).first()
            if m_any:
                unique_name = m_any.nome
                created_municipio = False
            else:
                # As last resort, create a municipio with an explicit id to avoid relying on autoincrement
                unique_name = f"TEST_MUN_{uuid.uuid4().hex[:8]}"
                m = Municipio(id=9999999, nome=unique_name, estado_id=estado.id)
                db.add(m)
                db.commit()
                db.refresh(m)
                created_municipio = True

        # create admin user
        admin_login = f"admin_loc_{uuid.uuid4().hex[:6]}"
        admin = SecUser(login=admin_login, pswd="x", active='Y', priv_admin='Y')
        db.add(admin)
        db.commit()

        # create produtor referencing the municipio and uf
        prod_id = uuid.uuid4().hex[:18]
        produtor = Produtor(
            id=prod_id,
            nome="Prod Test",
            municipio=unique_name,
            uf=estado.sigla
        )
        db.add(produtor)
        db.commit()

    finally:
        db.close()

    token = create_access_token({"sub": admin_login})
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"/api/produtores/{prod_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body.get('municipio') == unique_name
    # Expect nested municipio_info and uf_info present
    assert body.get('municipio_info') is not None
    assert body.get('uf_info') is not None

    # Cleanup
    db = SessionLocal()
    try:
        db.query(Produtor).filter(Produtor.id == prod_id).delete()
        if 'created_municipio' in locals() and created_municipio:
            db.query(Municipio).filter(Municipio.id == m.id).delete()
        db.query(SecUser).filter(SecUser.login == admin_login).delete()
        db.commit()
    finally:
        db.close()
