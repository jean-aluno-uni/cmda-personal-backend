from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def revoke(self, jti: str, expira_em: datetime) -> None:
        self.db.add(RevokedToken(jti=jti, expira_em=expira_em))
        self.db.commit()

    def is_revoked(self, jti: str) -> bool:
        stmt = select(RevokedToken.id).where(RevokedToken.jti == jti)
        return self.db.execute(stmt).scalar_one_or_none() is not None
