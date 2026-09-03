from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.timeutils import utcnow


class RevokedToken(Base):
    """Suporta RN-012: logout deve encerrar a sessão. JWT é stateless por padrão,
    então mantemos aqui a lista de tokens (por jti) revogados antes da expiração natural."""

    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column("RevokedTokenID", primary_key=True)
    jti: Mapped[str] = mapped_column("Jti", String(36), unique=True, nullable=False, index=True)
    expira_em: Mapped[datetime] = mapped_column("ExpiraEm", DateTime, nullable=False)
    revogado_em: Mapped[datetime] = mapped_column("RevogadoEm", DateTime, default=utcnow)
