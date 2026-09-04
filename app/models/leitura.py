from datetime import datetime

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utcnow


class Leitura(Base):
    __tablename__ = "leituras"

    id: Mapped[int] = mapped_column("LeituraID", primary_key=True)
    veiculo_id: Mapped[int] = mapped_column("VeiculoID", ForeignKey("veiculos.VeiculoID"), nullable=False, index=True)
    # default no python, nao no server -- servidor mysql local ta com hora diferente do UTC
    data_hora: Mapped[datetime] = mapped_column("DataHora", DateTime, default=utcnow, index=True)
    velocidade_kmh: Mapped[float | None] = mapped_column("VelocidadeKmh", DECIMAL(6, 2))
    rpm: Mapped[int | None] = mapped_column("Rpm", Integer)
    temp_motor_c: Mapped[float | None] = mapped_column("TempMotorC", DECIMAL(5, 2))
    temp_oleo_c: Mapped[float | None] = mapped_column("TempOleoC", DECIMAL(5, 2))
    temp_arrefecimento_c: Mapped[float | None] = mapped_column("TempArrefecimentoC", DECIMAL(5, 2))
    temp_ar_c: Mapped[float | None] = mapped_column("TempArC", DECIMAL(5, 2))
    tensao_bateria_v: Mapped[float | None] = mapped_column("TensaoBateriaV", DECIMAL(5, 2))

    veiculo: Mapped["Veiculo"] = relationship(back_populates="leituras")
