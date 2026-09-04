from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[int] = mapped_column("VeiculoID", primary_key=True)
    usuario_id: Mapped[int] = mapped_column("UsuarioID", ForeignKey("usuarios.UsuarioID"), nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column("Marca", String(60))
    modelo: Mapped[str | None] = mapped_column("Modelo", String(60))
    ano: Mapped[int | None] = mapped_column("Ano", Integer)
    placa: Mapped[str | None] = mapped_column("Placa", String(20))
    combustivel: Mapped[str | None] = mapped_column("Combustivel", String(20))

    conectado: Mapped[bool] = mapped_column("Conectado", Boolean, nullable=False, default=False)
    ultima_conexao: Mapped[datetime | None] = mapped_column("UltimaConexao", DateTime)

    usuario: Mapped["Usuario"] = relationship(back_populates="veiculos")
    leituras: Mapped[list["Leitura"]] = relationship(back_populates="veiculo", cascade="all, delete-orphan")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="veiculo", cascade="all, delete-orphan")
    diagnosticos: Mapped[list["Diagnostico"]] = relationship(back_populates="veiculo", cascade="all, delete-orphan")
