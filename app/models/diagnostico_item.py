from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DiagnosticoItem(Base):
    __tablename__ = "diagnostico_itens"

    id: Mapped[int] = mapped_column("DiagnosticoItemID", primary_key=True)
    diagnostico_id: Mapped[int] = mapped_column(
        "DiagnosticoID", ForeignKey("diagnosticos.DiagnosticoID"), nullable=False, index=True
    )
    indicador: Mapped[str] = mapped_column("Indicador", String(60), nullable=False)
    valor: Mapped[str] = mapped_column("Valor", String(120), nullable=False)
    observacao: Mapped[str | None] = mapped_column("Observacao", String(255))
    # Extensões ao ER original (Parte 18), necessárias para RF-013 (RN-008/RN-009):
    # faixa de referência exibida ao lado do valor e flag indicando item fora do esperado.
    referencia: Mapped[str | None] = mapped_column("Referencia", String(60))
    alerta: Mapped[bool] = mapped_column("Alerta", Boolean, nullable=False, default=False)

    diagnostico: Mapped["Diagnostico"] = relationship(back_populates="itens")
