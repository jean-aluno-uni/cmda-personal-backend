import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.usuario import Usuario
from app.models.veiculo import Veiculo
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.veiculo_repository import VeiculoRepository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciais is None:
        raise UnauthorizedError("Não autenticado")

    try:
        payload = decode_access_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise UnauthorizedError("Token inválido ou expirado")

    # token pode ainda nao ter expirado mas ja foi derrubado no logout
    if RevokedTokenRepository(db).is_revoked(payload["jti"]):
        raise UnauthorizedError("Sessão encerrada, faça login novamente")

    usuario = UsuarioRepository(db).get_by_id(int(payload["sub"]))
    if usuario is None:
        raise UnauthorizedError("Usuário não encontrado")

    return usuario


def get_current_token_payload(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    if credenciais is None:
        raise UnauthorizedError("Não autenticado")
    try:
        return decode_access_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise UnauthorizedError("Token inválido ou expirado")


def get_owned_vehicle(
    veiculo_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Veiculo:
    veiculo = VeiculoRepository(db).get_by_id(veiculo_id)
    if veiculo is None:
        raise NotFoundError("Veículo não encontrado")
    if veiculo.usuario_id != usuario_atual.id:
        raise ForbiddenError("Veículo não pertence ao usuário autenticado")
    return veiculo
