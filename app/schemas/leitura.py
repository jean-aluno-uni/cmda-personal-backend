from datetime import datetime

from app.schemas.common import CamelModel


class LeituraCreate(CamelModel):
    velocidade_kmh: float | None = None
    rpm: int | None = None
    temp_motor_c: float | None = None
    temp_oleo_c: float | None = None
    temp_arrefecimento_c: float | None = None
    temp_ar_c: float | None = None
    tensao_bateria_v: float | None = None
    data_hora: datetime | None = None


class TelemetriaLatestOut(CamelModel):
    disponivel: bool
    motivo: str | None = None
    velocidade_kmh: float | None = None
    rpm: int | None = None
    temp_geral: float | None = None
    temp_oleo: float | None = None
    temp_liquido: float | None = None
    temp_ar: float | None = None
    tensao_bateria_v: float | None = None
    data_hora: datetime | None = None


class TemperatureHistoryPoint(CamelModel):
    data_hora: datetime
    oleo: float | None
    liquido: float | None
    ar: float | None
    geral: float | None
