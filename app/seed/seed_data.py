"""Popula dados de demonstração. Rodar com: python -m app.seed.seed_data
Idempotente: pode ser executado várias vezes sem duplicar registros.
"""

from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.alerta import Alerta
from app.models.diagnostico import Diagnostico
from app.models.diagnostico_item import DiagnosticoItem
from app.models.leitura import Leitura
from app.models.usuario import Usuario
from app.models.veiculo import Veiculo


def get_or_create_usuario(db, nome, email, senha) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).one_or_none()
    if usuario is None:
        usuario = Usuario(nome_usuario=nome, email=email, senha_hash=hash_password(senha))
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        print(f"usuário criado: {email} / {senha}")
    else:
        print(f"usuário já existe: {email}")
    return usuario


def get_or_create_veiculo(db, usuario: Usuario, **dados) -> Veiculo:
    veiculo = (
        db.query(Veiculo)
        .filter(Veiculo.usuario_id == usuario.id, Veiculo.placa == dados["placa"])
        .one_or_none()
    )
    if veiculo is None:
        veiculo = Veiculo(usuario_id=usuario.id, **dados)
        db.add(veiculo)
        db.commit()
        db.refresh(veiculo)
        print(f"veículo criado: {dados['placa']}")
    else:
        print(f"veículo já existe: {dados['placa']}")
    return veiculo


def seed_leituras(db, veiculo: Veiculo) -> None:
    if db.query(Leitura).filter(Leitura.veiculo_id == veiculo.id).count() > 0:
        print("leituras já existem, pulando")
        return

    agora = datetime.now(timezone.utc)
    amostras = [
        (85, 1550, 83, 89, 30, 79, 12.5),
        (115, 2050, 89, 94, 31, 84, 12.6),
        (105, 1900, 87, 93, 30, 82, 12.8),
        (95, 1700, 86, 91, 29, 81, 12.7),
        (120, 2100, 90, 95, 30, 85, 12.6),
    ]
    for i, (vel, rpm, geral, oleo, ar, arref, tensao) in enumerate(reversed(amostras)):
        db.add(
            Leitura(
                veiculo_id=veiculo.id,
                data_hora=agora - timedelta(minutes=10 * (len(amostras) - i)),
                velocidade_kmh=vel,
                rpm=rpm,
                temp_motor_c=geral,
                temp_oleo_c=oleo,
                temp_ar_c=ar,
                temp_arrefecimento_c=arref,
                tensao_bateria_v=tensao,
            )
        )
    db.commit()
    print(f"{len(amostras)} leituras criadas")


def seed_alertas(db, veiculo: Veiculo) -> None:
    if db.query(Alerta).filter(Alerta.veiculo_id == veiculo.id).count() > 0:
        print("alertas já existem, pulando")
        return

    agora = datetime.now(timezone.utc)
    alertas = [
        ("Motor", "Temperatura do óleo elevada", "Óleo com temperatura acima do esperado", "high", agora - timedelta(minutes=30)),
        ("Motor", "RPM abaixo do esperado", "RPM abaixo do esperado para a velocidade atual", "high", agora - timedelta(minutes=50)),
        ("Transmissao", "Vibração detectada", "Vibração anômala detectada na transmissão", "medium", agora - timedelta(hours=1)),
        ("Bateria", "Tensão levemente baixa", "Tensão da bateria abaixo do ideal", "low", agora - timedelta(hours=2)),
    ]
    for origem, titulo, descricao, nivel, quando in alertas:
        db.add(Alerta(veiculo_id=veiculo.id, origem=origem, titulo=titulo, descricao=descricao, nivel=nivel, data_hora=quando))
    db.commit()
    print(f"{len(alertas)} alertas criados")


def seed_diagnostico(db, veiculo: Veiculo) -> None:
    if db.query(Diagnostico).filter(Diagnostico.veiculo_id == veiculo.id).count() > 0:
        print("diagnóstico já existe, pulando")
        return

    diagnostico = Diagnostico(veiculo_id=veiculo.id)
    diagnostico.itens = [
        DiagnosticoItem(indicador="RPM", valor="2.100", observacao="Normal", referencia="750 – 3.000 RPM", alerta=False),
        DiagnosticoItem(indicador="Velocidade", valor="120 km/h", observacao="Normal", referencia="0 – 200 km/h", alerta=False),
        DiagnosticoItem(indicador="Temp. geral", valor="80 °C", observacao="Normal", referencia="até 90 °C", alerta=False),
        DiagnosticoItem(indicador="Temp. ar admissão", valor="30 °C", observacao="Normal", referencia="até 40 °C", alerta=False),
        DiagnosticoItem(indicador="Temp. óleo", valor="90 °C", observacao="Temperatura elevada", referencia="até 85 °C", alerta=True),
        DiagnosticoItem(indicador="Temp. líquido arrefecimento", valor="30 °C", observacao="Normal", referencia="até 90 °C", alerta=False),
    ]
    db.add(diagnostico)
    db.commit()
    print("diagnóstico com 6 itens criado")


def run() -> None:
    db = SessionLocal()
    try:
        usuario_demo = get_or_create_usuario(db, "Amanda Pereira", "demo@cmda.app", "Demo@1234")
        veiculo_demo = get_or_create_veiculo(
            db,
            usuario_demo,
            marca="Fiat",
            modelo="Argo",
            ano=2022,
            placa="DEMO1A23",
            combustivel="Flex",
            conectado=True,
        )
        seed_leituras(db, veiculo_demo)
        seed_alertas(db, veiculo_demo)
        seed_diagnostico(db, veiculo_demo)

        # segundo usuario so pra eu testar manualmente que um nao acessa veiculo do outro
        outro_usuario = get_or_create_usuario(db, "Outro Motorista", "outro@cmda.app", "Outro@1234")
        get_or_create_veiculo(
            db,
            outro_usuario,
            marca="Hyundai",
            modelo="HB20",
            ano=2021,
            placa="OUTR0B99",
            combustivel="Flex",
            conectado=False,
        )

        print("\nSeed concluído.")
        print(f"Login demo: demo@cmda.app / Demo@1234 (veiculo_id={veiculo_demo.id})")
    finally:
        db.close()


if __name__ == "__main__":
    run()
