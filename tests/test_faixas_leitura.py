def _enviar(client, usuario_autenticado, leitura):
    veiculo_id = usuario_autenticado["veiculo_id"]
    resp = client.post(
        f"/api/v1/vehicles/{veiculo_id}/readings",
        headers=usuario_autenticado["headers"],
        json=leitura,
    )
    assert resp.status_code == 201


def _alertas(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    resp = client.get(f"/api/v1/vehicles/{veiculo_id}/alerts?period=24h", headers=usuario_autenticado["headers"])
    return resp.json()


def _diagnostico(client, usuario_autenticado):
    veiculo_id = usuario_autenticado["veiculo_id"]
    resp = client.get(f"/api/v1/vehicles/{veiculo_id}/diagnostics", headers=usuario_autenticado["headers"])
    return resp.json()


def test_leitura_normal_gera_diagnostico_sem_alerta(client, usuario_autenticado):
    _enviar(client, usuario_autenticado, {"rpm": 850, "tempArrefecimentoC": 90, "tensaoBateriaV": 14.2})

    assert _alertas(client, usuario_autenticado)["total"] == 0
    diagnostico = _diagnostico(client, usuario_autenticado)
    assert diagnostico["statusGeral"] is False
    assert len(diagnostico["itens"]) == 3


def test_leitura_fora_da_faixa_gera_alerta_e_diagnostico(client, usuario_autenticado):
    _enviar(client, usuario_autenticado, {"rpm": 850, "tempArrefecimentoC": 90, "tensaoBateriaV": 14.2})
    _enviar(client, usuario_autenticado, {"rpm": 850, "tempArrefecimentoC": 118, "tensaoBateriaV": 11.4})

    alertas = _alertas(client, usuario_autenticado)
    assert alertas["total"] == 2
    origens = {item["origem"] for item in alertas["items"]}
    assert origens == {"Motor", "Bateria"}

    diagnostico = _diagnostico(client, usuario_autenticado)
    assert diagnostico["statusGeral"] is True
    com_alerta = {item["indicador"] for item in diagnostico["itens"] if item["alerta"]}
    assert com_alerta == {"Temp. líquido arrefecimento", "Tensão da bateria"}


def test_valor_que_continua_fora_da_faixa_nao_repete_alerta(client, usuario_autenticado):
    for _ in range(3):
        _enviar(client, usuario_autenticado, {"rpm": 6600})

    assert _alertas(client, usuario_autenticado)["total"] == 1

    _enviar(client, usuario_autenticado, {"rpm": 850})
    _enviar(client, usuario_autenticado, {"rpm": 6600})

    assert _alertas(client, usuario_autenticado)["total"] == 2
