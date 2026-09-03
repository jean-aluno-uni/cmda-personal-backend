def test_registrar_leitura_e_consultar_latest(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    headers = usuario_autenticado["headers"]

    resp = client.post(
        f"/api/v1/vehicles/{veiculo_id}/readings",
        headers=headers,
        json={"velocidadeKmh": 100, "rpm": 1800, "tempMotorC": 85, "tempOleoC": 90},
    )
    assert resp.status_code == 201

    latest = client.get(f"/api/v1/vehicles/{veiculo_id}/telemetry/latest", headers=headers)
    assert latest.status_code == 200
    body = latest.json()
    assert body["disponivel"] is True
    assert body["rpm"] == 1800
    assert body["velocidadeKmh"] == 100


def test_veiculo_desconectado_nao_inventa_dado(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    headers = usuario_autenticado["headers"]

    client.post(f"/api/v1/vehicles/{veiculo_id}/readings", headers=headers, json={"rpm": 1800})
    client.post(f"/api/v1/vehicles/{veiculo_id}/disconnect", headers=headers)

    latest = client.get(f"/api/v1/vehicles/{veiculo_id}/telemetry/latest", headers=headers)

    assert latest.status_code == 200
    body = latest.json()
    assert body["disponivel"] is False
    assert body["motivo"] == "veiculo_desconectado"
    assert body["rpm"] is None
