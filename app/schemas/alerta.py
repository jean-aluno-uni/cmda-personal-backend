from datetime import datetime

from app.schemas.common import CamelModel


class AlertaCreate(CamelModel):
    origem: str
    titulo: str
    descricao: str | None = None
    nivel: str
    data_hora: datetime | None = None


class AlertaOut(CamelModel):
    id: int
    origem: str
    titulo: str
    descricao: str | None
    nivel: str
    status: str
    data_hora: datetime


class OrigemAlertaResumo(CamelModel):
    local: str
    percentual: float
    cor: str


class AlertaSummaryOut(CamelModel):
    total: int
    origem_alertas: list[OrigemAlertaResumo]
    tabela_alertas: list[AlertaOut]


class AlertaListOut(CamelModel):
    items: list[AlertaOut]
    total: int
    page: int
    page_size: int
