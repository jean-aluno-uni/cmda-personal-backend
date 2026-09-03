def test_criar_alerta_aparece_na_listagem_e_no_resumo(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    headers = usuario_autenticado["headers"]

    resp = client.post(
        f"/api/v1/vehicles/{veiculo_id}/alerts",
        headers=headers,
        json={"origem": "Motor", "titulo": "Temperatura elevada", "nivel": "high"},
    )
    assert resp.status_code == 201

    listagem = client.get(f"/api/v1/vehicles/{veiculo_id}/alerts?period=24h", headers=headers)
    assert listagem.status_code == 200
    body = listagem.json()
    assert body["total"] == 1
    assert body["items"][0]["titulo"] == "Temperatura elevada"

    resumo = client.get(f"/api/v1/vehicles/{veiculo_id}/alerts/summary?period=24h", headers=headers)
    assert resumo.status_code == 200
    resumo_body = resumo.json()
    assert resumo_body["total"] == 1
    assert resumo_body["origemAlertas"][0]["local"] == "Motor"
    assert resumo_body["origemAlertas"][0]["percentual"] == 100.0
