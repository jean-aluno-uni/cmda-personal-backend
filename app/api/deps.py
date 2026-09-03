import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
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
    """RN-001: acesso às funcionalidades internas só para usuários autenticados."""
    if credenciais is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")

    try:
        payload = decode_access_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado")

    # RN-012: token revogado por logout não pode mais ser usado, mesmo que ainda não
    # tenha expirado naturalmente.
    if RevokedTokenRepository(db).is_revoked(payload["jti"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão encerrada, faça login novamente")

    usuario = UsuarioRepository(db).get_by_id(int(payload["sub"]))
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado")

    return usuario


def get_current_token_payload(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    if credenciais is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
    try:
        return decode_access_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado")


def get_owned_vehicle(
    veiculo_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Veiculo:
    """RN-004/RN-011: leituras, alertas e diagnósticos (e o próprio veículo) só podem
    ser acessados pelo usuário dono do veículo."""
    veiculo = VeiculoRepository(db).get_by_id(veiculo_id)
    if veiculo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veículo não encontrado")
    if veiculo.usuario_id != usuario_atual.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Veículo não pertence ao usuário autenticado")
    return veiculo
