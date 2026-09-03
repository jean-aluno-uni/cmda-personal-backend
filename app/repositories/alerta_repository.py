from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.timeutils import to_utc_naive, utcnow
from app.models.alerta import Alerta


class AlertaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, veiculo_id: int, dados: dict) -> Alerta:
        dados = dict(dados)
        dados["data_hora"] = to_utc_naive(dados["data_hora"]) if dados.get("data_hora") else utcnow()
        alerta = Alerta(veiculo_id=veiculo_id, **dados)
        self.db.add(alerta)
        self.db.commit()
        self.db.refresh(alerta)
        return alerta

    def list_by_periodo(self, veiculo_id: int, desde: datetime, page: int, page_size: int) -> tuple[list[Alerta], int]:
        base_stmt = select(Alerta).where(Alerta.veiculo_id == veiculo_id, Alerta.data_hora >= desde)

        total = self.db.execute(
            select(func.count()).select_from(base_stmt.order_by(None).subquery())
        ).scalar_one()

        stmt = base_stmt.order_by(Alerta.data_hora.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def resumo_por_origem(self, veiculo_id: int, desde: datetime) -> list[tuple[str, int]]:
        stmt = (
            select(Alerta.origem, func.count().label("total"))
            .where(Alerta.veiculo_id == veiculo_id, Alerta.data_hora >= desde)
            .group_by(Alerta.origem)
        )
        return list(self.db.execute(stmt).all())
