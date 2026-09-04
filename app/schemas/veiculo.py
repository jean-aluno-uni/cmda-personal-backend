from typing import Optional

from app.schemas.common import CamelModel


class VeiculoOut(CamelModel):
    id: int
    marca: Optional[str]
    modelo: Optional[str]
    ano: Optional[int]
    placa: Optional[str]
    combustivel: Optional[str]
    conectado: bool


class VeiculoStatusOut(CamelModel):
    conectado: bool
    modelo: Optional[str]
    placa: Optional[str]
    marca: Optional[str]
    ano: Optional[int]


class ConexaoResponse(CamelModel):
    conectado: bool
