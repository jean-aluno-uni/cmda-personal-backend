from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo
from app.repositories.veiculo_repository import VeiculoRepository


class VeiculoService:
    """RN-004/RN-005: dados do veículo vinculados ao usuário autenticado (a posse já é
    validada antes de chegar aqui, via dependency `get_owned_vehicle`), e o sistema deve
    refletir corretamente o estado de conexão."""

    def __init__(self, db: Session):
        self.repo = VeiculoRepository(db)

    def connect(self, veiculo: Veiculo) -> Veiculo:
        return self.repo.set_conectado(veiculo, True)

    def disconnect(self, veiculo: Veiculo) -> Veiculo:
        return self.repo.set_conectado(veiculo, False)
