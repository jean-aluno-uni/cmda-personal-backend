from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutils import to_utc_naive, utcnow
from app.models.leitura import Leitura


class LeituraRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, veiculo_id: int, dados: dict) -> Leitura:
        dados = dict(dados)
        dados["data_hora"] = to_utc_naive(dados["data_hora"]) if dados.get("data_hora") else utcnow()
        leitura = Leitura(veiculo_id=veiculo_id, **dados)
        self.db.add(leitura)
        self.db.flush()
        return leitura

    def get_latest(self, veiculo_id: int) -> Leitura | None:
        stmt = (
            select(Leitura)
            .where(Leitura.veiculo_id == veiculo_id)
            .order_by(Leitura.data_hora.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_history(self, veiculo_id: int, desde: datetime, limite: int = 50) -> list[Leitura]:
        stmt = (
            select(Leitura)
            .where(Leitura.veiculo_id == veiculo_id, Leitura.data_hora >= desde)
            .order_by(Leitura.data_hora.asc())
            .limit(limite)
        )
        return list(self.db.execute(stmt).scalars().all())
