from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token_payload, get_current_user
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    OtpResendRequest,
    OtpVerifyRequest,
    OtpVerifyResponse,
    ResetPasswordRequest,
)
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario, token = AuthService(db).login(dados.email, dados.senha)
    return LoginResponse(access_token=token, usuario=UsuarioOut.from_model(usuario))


@router.get("/me", response_model=UsuarioOut)
def me(usuario_atual: Usuario = Depends(get_current_user)):
    return UsuarioOut.from_model(usuario_atual)


@router.post("/password/forgot", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(dados: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).forgot_password(dados.email)


@router.post("/password/otp/resend", status_code=status.HTTP_204_NO_CONTENT)
def resend_otp(dados: OtpResendRequest, db: Session = Depends(get_db)):
    AuthService(db).resend_otp(dados.email)


@router.post("/password/otp/verify", response_model=OtpVerifyResponse)
def verify_otp(dados: OtpVerifyRequest, db: Session = Depends(get_db)):
    reset_token = AuthService(db).verify_otp(dados.email, dados.codigo)
    return OtpVerifyResponse(reset_token=reset_token)


@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(dados: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(dados.reset_token, dados.nova_senha)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token_payload: dict = Depends(get_current_token_payload),
    _usuario_atual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).logout(token_payload["jti"], token_payload["exp"])
