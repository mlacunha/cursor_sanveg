from uuid import uuid4

from app.models.users import User
from app.utils.security import create_access_token, get_password_hash


def _make_user(**overrides) -> User:
    data = {
        "id": overrides.pop("id", str(uuid4())),
        "login": overrides.pop("login", f"user-{uuid4().hex[:8]}"),
        "password": overrides.pop("password", get_password_hash("Senha@123")),
        "nome": overrides.pop("nome", "Usuario Teste"),
        "email": overrides.pop("email", f"{uuid4().hex[:8]}@example.com"),
        "active": overrides.pop("active", True),
        "role": overrides.pop("role", "comum"),
        "id_orgao": overrides.pop("id_orgao", None),
    }
    data.update(overrides)
    return User(**data)


def _auth_header(user: User) -> dict[str, str]:
    token = create_access_token({"sub": user.login})
    return {"Authorization": f"Bearer {token}"}


def test_sync_push_keeps_successful_items_when_next_item_fails(client, db_session):
    admin = _make_user(login="admin-sync", email="admin-sync@example.com", role="superusuario")
    existing = _make_user(login="dup-login", email="dup@example.com")
    db_session.add_all([admin, existing])
    db_session.commit()

    first_payload = {
        "id": str(uuid4()),
        "login": "novo-login",
        "email": "novo@example.com",
        "nome": "Novo Usuario",
        "password": "Senha@123",
    }
    second_payload = {
        "id": str(uuid4()),
        "login": "outro-login",
        "email": "dup@example.com",
        "nome": "Usuario Duplicado",
        "password": "Senha@123",
    }

    response = client.post(
        "/api/sync/push",
        json={
            "queue": [
                {"id": 1, "action": "put", "route": "usuarios", "payload": first_payload, "timestamp": 1},
                {"id": 2, "action": "put", "route": "usuarios", "payload": second_payload, "timestamp": 2},
            ]
        },
        headers=_auth_header(admin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["processed_ids"] == [1]
    assert body["errors"][0]["id"] == 2

    saved = db_session.get(User, first_payload["id"])
    assert saved is not None
    assert saved.email == "novo@example.com"


def test_sync_push_preserves_login_on_email_update_without_login_field(client, db_session):
    admin = _make_user(login="admin-email", email="admin-email@example.com", role="superusuario")
    target = _make_user(login="login-antigo", email="antigo@example.com")
    db_session.add_all([admin, target])
    db_session.commit()

    response = client.post(
        "/api/sync/push",
        json={
            "queue": [
                {
                    "id": 1,
                    "action": "put",
                    "route": "usuarios",
                    "payload": {
                        "id": target.id,
                        "email": "novo@example.com",
                        "nome": "Nome Atualizado",
                    },
                    "timestamp": 1,
                }
            ]
        },
        headers=_auth_header(admin),
    )

    assert response.status_code == 200
    assert response.json()["processed_ids"] == [1]

    db_session.refresh(target)
    assert target.email == "novo@example.com"
    assert target.login == "login-antigo"


def test_sync_push_blocks_regular_user_from_updating_other_user(client, db_session):
    current_user = _make_user(login="comum-sync", email="comum-sync@example.com", role="comum")
    other_user = _make_user(login="outro-sync", email="outro-sync@example.com", role="comum")
    db_session.add_all([current_user, other_user])
    db_session.commit()

    response = client.post(
        "/api/sync/push",
        json={
            "queue": [
                {
                    "id": 1,
                    "action": "put",
                    "route": "usuarios",
                    "payload": {
                        "id": other_user.id,
                        "nome": "Tentativa Indevida",
                    },
                    "timestamp": 1,
                }
            ]
        },
        headers=_auth_header(current_user),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["processed_ids"] == []
    assert "proprio cadastro" in body["errors"][0]["error"]

    db_session.refresh(other_user)
    assert other_user.nome != "Tentativa Indevida"
