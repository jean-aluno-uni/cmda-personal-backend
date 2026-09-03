from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models.password_reset import PasswordReset


class PasswordResetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, usuario_id: int, codigo_otp: str, expira_em: datetime) -> PasswordReset:
        registro = PasswordReset(usuario_id=usuario_id, codigo_otp=codigo_otp, expira_em=expira_em)
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def get_ultimo_pendente(self, usuario_id: int) -> PasswordReset | None:
        stmt = (
            select(PasswordReset)
            .where(PasswordReset.usuario_id == usuario_id, PasswordReset.usado.is_(False))
            .order_by(PasswordReset.criado_em.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_reset_token(self, reset_token: str) -> PasswordReset | None:
        stmt = select(PasswordReset).where(PasswordReset.reset_token == reset_token)
        return self.db.execute(stmt).scalar_one_or_none()

    def marcar_usado(self, registro: PasswordReset) -> None:
        registro.usado = True
        self.db.commit()

    def definir_reset_token(self, registro: PasswordReset, reset_token: str, expira_em: datetime) -> None:
        registro.reset_token = reset_token
        registro.expira_em = expira_em
        self.db.commit()

    @staticmethod
    def esta_expirado(registro: PasswordReset) -> bool:
        return utcnow() > registro.expira_em
