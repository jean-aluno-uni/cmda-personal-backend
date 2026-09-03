def test_dono_acessa_proprio_veiculo(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    resp = client.get(f"/api/v1/vehicles/{veiculo_id}", headers=usuario_autenticado["headers"])
    assert resp.status_code == 200
    assert resp.json()["placa"] == "AAA0A00"


def test_usuario_nao_acessa_veiculo_de_outro(client, usuario_autenticado, outro_usuario_com_veiculo):
    _outro_usuario, veiculo_de_outro = outro_usuario_com_veiculo

    resp = client.get(f"/api/v1/vehicles/{veiculo_de_outro.id}", headers=usuario_autenticado["headers"])

    assert resp.status_code == 403


def test_veiculo_inexistente_retorna_404(client, usuario_autenticado):
    resp = client.get("/api/v1/vehicles/99999", headers=usuario_autenticado["headers"])
    assert resp.status_code == 404


def test_post_readings_em_veiculo_de_outro_e_bloqueado(client, usuario_autenticado, outro_usuario_com_veiculo):
    _outro_usuario, veiculo_de_outro = outro_usuario_com_veiculo

    resp = client.post(
        f"/api/v1/vehicles/{veiculo_de_outro.id}/readings",
        headers=usuario_autenticado["headers"],
        json={"rpm": 2000},
    )

    assert resp.status_code == 403


def test_connect_disconnect(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    headers = usuario_autenticado["headers"]

    resp = client.post(f"/api/v1/vehicles/{veiculo_id}/disconnect", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["conectado"] is False

    resp = client.post(f"/api/v1/vehicles/{veiculo_id}/connect", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["conectado"] is True
