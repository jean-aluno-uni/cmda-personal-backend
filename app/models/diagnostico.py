from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utcnow


class Diagnostico(Base):
    __tablename__ = "diagnosticos"

    id: Mapped[int] = mapped_column("DiagnosticoID", primary_key=True)
    veiculo_id: Mapped[int] = mapped_column("VeiculoID", ForeignKey("veiculos.VeiculoID"), nullable=False, index=True)
    data_hora: Mapped[datetime] = mapped_column("DataHora", DateTime, default=utcnow, index=True)

    veiculo: Mapped["Veiculo"] = relationship(back_populates="diagnosticos")
    itens: Mapped[list["DiagnosticoItem"]] = relationship(back_populates="diagnostico", cascade="all, delete-orphan")
