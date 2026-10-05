def test_lista_apenas_veiculos_do_usuario_logado(client, usuario_autenticado, outro_usuario_com_veiculo):
    _outro_usuario, veiculo_de_outro = outro_usuario_com_veiculo

    resp = client.get("/api/v1/vehicles", headers=usuario_autenticado["headers"])

    assert resp.status_code == 200
    veiculos = resp.json()
    assert len(veiculos) == 1
    assert veiculos[0]["id"] == usuario_autenticado["veiculo_id"]
    assert veiculos[0]["placa"] == "AAA0A00"
    assert veiculo_de_outro.id not in [v["id"] for v in veiculos]


def test_lista_veiculos_em_camel_case(client, usuario_autenticado):
    resp = client.get("/api/v1/vehicles", headers=usuario_autenticado["headers"])

    assert set(resp.json()[0].keys()) == {"id", "marca", "modelo", "ano", "placa", "combustivel", "conectado"}


def test_lista_veiculos_sem_token_retorna_401(client):
    resp = client.get("/api/v1/vehicles")

    assert resp.status_code == 401
    assert "error" in resp.json()
