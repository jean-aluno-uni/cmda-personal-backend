from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UsuarioOut)
def me(usuario_atual: Usuario = Depends(get_current_user)):
    return UsuarioOut.from_model(usuario_atual)
