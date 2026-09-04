from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.timeutils import utcnow


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id: Mapped[int] = mapped_column("PasswordResetID", primary_key=True)
    usuario_id: Mapped[int] = mapped_column("UsuarioID", ForeignKey("usuarios.UsuarioID"), nullable=False, index=True)
    codigo_otp: Mapped[str] = mapped_column("CodigoOtp", String(6), nullable=False)
    reset_token: Mapped[str | None] = mapped_column("ResetToken", String(255), unique=True)
    expira_em: Mapped[datetime] = mapped_column("ExpiraEm", DateTime, nullable=False)
    usado: Mapped[bool] = mapped_column("Usado", Boolean, nullable=False, default=False)
    criado_em: Mapped[datetime] = mapped_column("CriadoEm", DateTime, default=utcnow)

    usuario: Mapped["Usuario"] = relationship()
