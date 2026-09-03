from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utcnow


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column("UsuarioID", primary_key=True)
    nome_usuario: Mapped[str] = mapped_column("NomeUsuario", String(100), nullable=False)
    email: Mapped[str] = mapped_column("Email", String(150), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column("SenhaHash", String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        "Role", Enum("motorista", "admin", name="usuario_role"), nullable=False, default="motorista"
    )
    criado_em: Mapped[datetime] = mapped_column("CriadoEm", DateTime, default=utcnow)

    veiculos: Mapped[list["Veiculo"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
