from app.schemas.common import CamelModel


class VeiculoOut(CamelModel):
    id: int
    marca: str | None
    modelo: str | None
    ano: int | None
    placa: str | None
    combustivel: str | None
    conectado: bool


class VeiculoStatusOut(CamelModel):
    conectado: bool
    modelo: str | None
    placa: str | None
    marca: str | None
    ano: int | None


class ConexaoResponse(CamelModel):
    conectado: bool
