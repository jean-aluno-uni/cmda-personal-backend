from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models.veiculo import Veiculo
from app.repositories.alerta_repository import AlertaRepository
from app.repositories.diagnostico_repository import DiagnosticoRepository
from app.repositories.leitura_repository import LeituraRepository
from app.schemas.leitura import LeituraCreate, TelemetriaLatestOut, TemperatureHistoryPoint

_RANGE_PARA_TIMEDELTA = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}

_FAIXAS = [
    ("rpm", "RPM", "Motor", 600, 4000, "RPM"),
    ("velocidade_kmh", "Velocidade", "Motor", None, 120, "km/h"),
    ("temp_motor_c", "Temp. geral", "Motor", None, 110, "°C"),
    ("temp_oleo_c", "Temp. óleo", "Motor", None, 120, "°C"),
    ("temp_arrefecimento_c", "Temp. líquido arrefecimento", "Motor", None, 105, "°C"),
    ("temp_ar_c", "Temp. ar admissão", "Motor", None, 45, "°C"),
    ("tensao_bateria_v", "Tensão da bateria", "Bateria", 12, 15, "V"),
]


def _numero(valor) -> str:
    valor = float(valor)
    return f"{valor:.1f}".replace(".", ",") if valor % 1 else f"{valor:.0f}"


def _referencia(minimo, maximo, unidade) -> str:
    if minimo is None:
        return f"até {_numero(maximo)} {unidade}"
    return f"{_numero(minimo)} a {_numero(maximo)} {unidade}"


def _situacao(valor, minimo, maximo) -> str | None:
    if valor is None:
        return None
    if minimo is not None and valor < minimo:
        return "abaixo"
    if valor > maximo:
        return "acima"
    return "normal"


class TelemetriaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LeituraRepository(db)

    def registrar_leitura(self, veiculo_id: int, dados: LeituraCreate):
        payload = dados.model_dump(exclude_none=True)
        anterior = self.repo.get_latest(veiculo_id)
        leitura = self.repo.create(veiculo_id, payload)
        self._avaliar_faixas(veiculo_id, anterior, leitura)
        self.db.commit()
        return leitura

    def _avaliar_faixas(self, veiculo_id: int, anterior, leitura) -> None:
        itens = []
        for campo, indicador, origem, minimo, maximo, unidade in _FAIXAS:
            valor = getattr(leitura, campo)
            situacao = _situacao(valor, minimo, maximo)
            if situacao is None:
                continue
            situacao_anterior = _situacao(getattr(anterior, campo), minimo, maximo) if anterior else None
            referencia = _referencia(minimo, maximo, unidade)
            if situacao != situacao_anterior and situacao != "normal":
                AlertaRepository(self.db).create(veiculo_id, {
                    "origem": origem,
                    "titulo": f"{indicador} {situacao} do esperado",
                    "descricao": f"{indicador} em {_numero(valor)} {unidade}, referência {referencia}",
                    "nivel": "high",
                    "data_hora": leitura.data_hora,
                })
            itens.append({
                "indicador": indicador,
                "valor": f"{_numero(valor)} {unidade}",
                "observacao": "Normal" if situacao == "normal" else f"{situacao.capitalize()} do esperado",
                "referencia": referencia,
                "alerta": situacao != "normal",
            })
        if itens:
            DiagnosticoRepository(self.db).create(veiculo_id, leitura.data_hora, itens)

    def obter_ultima(self, veiculo: Veiculo) -> TelemetriaLatestOut:
        if not veiculo.conectado:
            return TelemetriaLatestOut(disponivel=False, motivo="veiculo_desconectado")

        leitura = self.repo.get_latest(veiculo.id)
        if leitura is None:
            return TelemetriaLatestOut(disponivel=False, motivo="sem_leituras")

        return TelemetriaLatestOut(
            disponivel=True,
            velocidade_kmh=leitura.velocidade_kmh,
            rpm=leitura.rpm,
            temp_geral=leitura.temp_motor_c,
            temp_oleo=leitura.temp_oleo_c,
            temp_liquido=leitura.temp_arrefecimento_c,
            temp_ar=leitura.temp_ar_c,
            tensao_bateria_v=leitura.tensao_bateria_v,
            data_hora=leitura.data_hora,
        )

    def obter_historico_temperatura(self, veiculo_id: int, range_str: str) -> list[TemperatureHistoryPoint]:
        delta = _RANGE_PARA_TIMEDELTA.get(range_str, _RANGE_PARA_TIMEDELTA["7d"])
        desde = utcnow() - delta
        leituras = self.repo.get_history(veiculo_id, desde)
        return [
            TemperatureHistoryPoint(
                data_hora=leitura.data_hora,
                oleo=leitura.temp_oleo_c,
                liquido=leitura.temp_arrefecimento_c,
                ar=leitura.temp_ar_c,
                geral=leitura.temp_motor_c,
            )
            for leitura in leituras
        ]
