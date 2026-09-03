from datetime import datetime

from app.schemas.common import CamelModel


class DiagnosticoItemCreate(CamelModel):
    indicador: str
    valor: str
    observacao: str | None = None
    referencia: str | None = None
    alerta: bool = False


class DiagnosticoItemOut(CamelModel):
    indicador: str
    valor: str
    observacao: str | None
    referencia: str | None
    alerta: bool


class DiagnosticoCreate(CamelModel):
    data_hora: datetime | None = None
    itens: list[DiagnosticoItemCreate]


class DiagnosticoOut(CamelModel):
    id: int
    data_hora: datetime
    status_geral: bool
    itens: list[DiagnosticoItemOut]
