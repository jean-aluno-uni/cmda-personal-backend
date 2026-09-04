from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo
from app.repositories.veiculo_repository import VeiculoRepository


class VeiculoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VeiculoRepository(db)

    def connect(self, veiculo: Veiculo) -> Veiculo:
        veiculo = self.repo.set_conectado(veiculo, True)
        self.db.commit()
        return veiculo

    def disconnect(self, veiculo: Veiculo) -> Veiculo:
        veiculo = self.repo.set_conectado(veiculo, False)
        self.db.commit()
        return veiculo
