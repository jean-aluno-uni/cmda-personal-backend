from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.timeutils import to_utc_naive, utcnow
from app.models.diagnostico import Diagnostico
from app.models.diagnostico_item import DiagnosticoItem


class DiagnosticoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest(self, veiculo_id: int) -> Diagnostico | None:
        stmt = (
            select(Diagnostico)
            .where(Diagnostico.veiculo_id == veiculo_id)
            .options(selectinload(Diagnostico.itens))
            .order_by(Diagnostico.data_hora.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, veiculo_id: int, data_hora, itens: list[dict]) -> Diagnostico:
        diagnostico = Diagnostico(veiculo_id=veiculo_id)
        diagnostico.data_hora = to_utc_naive(data_hora) if data_hora is not None else utcnow()
        diagnostico.itens = [DiagnosticoItem(**item) for item in itens]
        self.db.add(diagnostico)
        self.db.flush()
        return diagnostico
