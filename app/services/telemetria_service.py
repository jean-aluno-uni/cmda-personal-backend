from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models.veiculo import Veiculo
from app.repositories.leitura_repository import LeituraRepository
from app.schemas.leitura import LeituraCreate, TelemetriaLatestOut, TemperatureHistoryPoint

_RANGE_PARA_TIMEDELTA = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


class TelemetriaService:
    """RN-004/RN-005: leituras vinculadas a um veículo específico; se o veículo não está
    conectado, o sistema informa a indisponibilidade em vez de inventar dado."""

    def __init__(self, db: Session):
        self.repo = LeituraRepository(db)

    def registrar_leitura(self, veiculo_id: int, dados: LeituraCreate):
        payload = dados.model_dump(exclude_none=True)
        return self.repo.create(veiculo_id, payload)

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
