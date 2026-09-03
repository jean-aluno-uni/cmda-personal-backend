import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.timeutils import to_utc_naive, utcnow
from app.core.security import (
    create_access_token,
    generate_otp_code,
    generate_reset_token,
    hash_password,
    verify_password,
)
from app.models.usuario import Usuario
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.usuario_repository import UsuarioRepository

logger = logging.getLogger("cmda.auth")


class AuthService:
    """Regras de negócio de autenticação: RN-001 (acesso só autenticado), RN-002 (conta
    individual), RN-003 (recuperação de senha via código/token temporário) e RN-012
    (logout encerra a sessão)."""

    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)
        self.resets = PasswordResetRepository(db)
        self.revoked = RevokedTokenRepository(db)

    def login(self, email: str, senha: str) -> tuple[Usuario, str]:
        usuario = self.usuarios.get_by_email(email)
        if usuario is None or not verify_password(senha, usuario.senha_hash):
            raise UnauthorizedError("Credenciais inválidas")
        token = create_access_token(usuario.id, usuario.role)
        return usuario, token

    def _emitir_novo_otp(self, usuario: Usuario) -> None:
        pendente = self.resets.get_ultimo_pendente(usuario.id)
        if pendente is not None:
            self.resets.marcar_usado(pendente)

        codigo = generate_otp_code()
        expira_em = utcnow() + timedelta(minutes=settings.otp_expire_minutes)
        self.resets.create(usuario.id, codigo, expira_em)

        # Requisito da Fase 01: não precisa enviar e-mail de verdade, basta logar.
        logger.info("OTP de recuperação de senha para %s: %s", usuario.email, codigo)

    def forgot_password(self, email: str) -> None:
        usuario = self.usuarios.get_by_email(email)
        if usuario is not None:
            self._emitir_novo_otp(usuario)
        # Resposta sempre "sucesso" independente de o e-mail existir, para não
        # revelar quais e-mails têm conta (evita enumeração de usuários).

    def resend_otp(self, email: str) -> None:
        self.forgot_password(email)

    def verify_otp(self, email: str, codigo: str) -> str:
        usuario = self.usuarios.get_by_email(email)
        if usuario is None:
            raise UnauthorizedError("Código inválido ou expirado")

        pendente = self.resets.get_ultimo_pendente(usuario.id)
        if pendente is None or pendente.codigo_otp != codigo or self.resets.esta_expirado(pendente):
            raise UnauthorizedError("Código inválido ou expirado")

        reset_token = generate_reset_token()
        expira_em = utcnow() + timedelta(minutes=settings.reset_token_expire_minutes)
        self.resets.definir_reset_token(pendente, reset_token, expira_em)
        return reset_token

    def reset_password(self, reset_token: str, nova_senha: str) -> None:
        registro = self.resets.get_by_reset_token(reset_token)
        if registro is None or registro.usado or self.resets.esta_expirado(registro):
            raise UnauthorizedError("Token de redefinição inválido ou expirado")

        usuario = self.usuarios.get_by_id(registro.usuario_id)
        self.usuarios.update_senha(usuario, hash_password(nova_senha))
        self.resets.marcar_usado(registro)  # token de uso único (RN-003)

    def logout(self, jti: str, exp_timestamp: int) -> None:
        expira_em = to_utc_naive(datetime.fromtimestamp(exp_timestamp, tz=timezone.utc))
        self.revoked.revoke(jti, expira_em)
