from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models.veiculo import Veiculo


class VeiculoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, veiculo_id: int) -> Veiculo | None:
        return self.db.get(Veiculo, veiculo_id)

    def list_by_usuario(self, usuario_id: int) -> list[Veiculo]:
        return self.db.query(Veiculo).filter(Veiculo.usuario_id == usuario_id).all()

    def create(self, usuario_id: int, **kwargs) -> Veiculo:
        veiculo = Veiculo(usuario_id=usuario_id, **kwargs)
        self.db.add(veiculo)
        self.db.flush()
        return veiculo

    def set_conectado(self, veiculo: Veiculo, conectado: bool) -> Veiculo:
        veiculo.conectado = conectado
        if conectado:
            veiculo.ultima_conexao = utcnow()
        return veiculo
