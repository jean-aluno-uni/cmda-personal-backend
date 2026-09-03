from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utcnow


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column("AlertaID", primary_key=True)
    veiculo_id: Mapped[int] = mapped_column("VeiculoID", ForeignKey("veiculos.VeiculoID"), nullable=False, index=True)
    data_hora: Mapped[datetime] = mapped_column("DataHora", DateTime, default=utcnow, index=True)
    origem: Mapped[str] = mapped_column("Origem", String(30), nullable=False)
    titulo: Mapped[str] = mapped_column("Titulo", String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column("Descricao", Text)
    nivel: Mapped[str] = mapped_column("Nivel", String(20), nullable=False)
    status: Mapped[str] = mapped_column("Status", String(20), nullable=False, default="Ativo")

    veiculo: Mapped["Veiculo"] = relationship(back_populates="alertas")
