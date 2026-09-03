import re


def test_login_com_sucesso(client, db_session):
    from app.core.security import hash_password
    from app.models.usuario import Usuario

    db_session.add(Usuario(nome_usuario="Fulano", email="fulano@teste.com", senha_hash=hash_password("Senha@123")))
    db_session.commit()

    resp = client.post("/api/v1/auth/login", json={"email": "fulano@teste.com", "senha": "Senha@123"})

    assert resp.status_code == 200
    body = resp.json()
    assert "accessToken" in body
    assert body["usuario"]["email"] == "fulano@teste.com"


def test_login_com_senha_errada(client, db_session):
    from app.core.security import hash_password
    from app.models.usuario import Usuario

    db_session.add(Usuario(nome_usuario="Fulano", email="fulano@teste.com", senha_hash=hash_password("Senha@123")))
    db_session.commit()

    resp = client.post("/api/v1/auth/login", json={"email": "fulano@teste.com", "senha": "errada"})

    assert resp.status_code == 401


def test_me_sem_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_com_token(client, usuario_autenticado):
    resp = client.get("/api/v1/auth/me", headers=usuario_autenticado["headers"])
    assert resp.status_code == 200
    assert resp.json()["email"] == "motorista@teste.com"


def test_fluxo_completo_recuperacao_de_senha(client, db_session, caplog):
    from app.core.security import hash_password
    from app.models.usuario import Usuario

    db_session.add(Usuario(nome_usuario="Fulano", email="fulano@teste.com", senha_hash=hash_password("Senha@123")))
    db_session.commit()

    with caplog.at_level("INFO", logger="cmda.auth"):
        resp = client.post("/api/v1/auth/password/forgot", json={"email": "fulano@teste.com"})
    assert resp.status_code == 204

    codigo = re.search(r"(\d{6})", caplog.text).group(1)

    verify_resp = client.post(
        "/api/v1/auth/password/otp/verify", json={"email": "fulano@teste.com", "codigo": codigo}
    )
    assert verify_resp.status_code == 200
    reset_token = verify_resp.json()["resetToken"]

    reset_resp = client.post(
        "/api/v1/auth/password/reset", json={"resetToken": reset_token, "novaSenha": "NovaSenha@1"}
    )
    assert reset_resp.status_code == 204

    login_antigo = client.post("/api/v1/auth/login", json={"email": "fulano@teste.com", "senha": "Senha@123"})
    assert login_antigo.status_code == 401

    login_novo = client.post("/api/v1/auth/login", json={"email": "fulano@teste.com", "senha": "NovaSenha@1"})
    assert login_novo.status_code == 200

    # token de reset já usado não pode ser reaproveitado (RN-003)
    reset_reuso = client.post(
        "/api/v1/auth/password/reset", json={"resetToken": reset_token, "novaSenha": "Outra@1234"}
    )
    assert reset_reuso.status_code == 401


def test_reset_com_senha_fraca_e_rejeitado(client):
    resp = client.post(
        "/api/v1/auth/password/reset", json={"resetToken": "qualquer", "novaSenha": "abc123"}
    )
    assert resp.status_code == 422


def test_logout_invalida_token(client, usuario_autenticado):
    headers = usuario_autenticado["headers"]

    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 204

    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 401
