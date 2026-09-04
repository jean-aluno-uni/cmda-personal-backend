import re

from pydantic import EmailStr, field_validator

from app.schemas.common import CamelModel
from app.schemas.usuario import UsuarioOut

_SPECIAL_CHARS = r"!@#$%^&*(),.?\":{}|<>"


def validar_regras_senha(senha: str) -> list[str]:
    erros = []
    if len(senha) < 8:
        erros.append("mínimo 8 caracteres")
    if not re.search(r"[a-z]", senha):
        erros.append("ao menos 1 letra minúscula")
    if not re.search(r"[A-Z]", senha):
        erros.append("ao menos 1 letra maiúscula")
    if not re.search(r"[0-9]", senha):
        erros.append("ao menos 1 número")
    if not re.search(f"[{re.escape(_SPECIAL_CHARS)}]", senha):
        erros.append("ao menos 1 caractere especial")
    return erros


class LoginRequest(CamelModel):
    email: EmailStr
    senha: str


class LoginResponse(CamelModel):
    access_token: str
    usuario: UsuarioOut


class ForgotPasswordRequest(CamelModel):
    email: EmailStr


class OtpResendRequest(CamelModel):
    email: EmailStr


class OtpVerifyRequest(CamelModel):
    email: EmailStr
    codigo: str


class OtpVerifyResponse(CamelModel):
    reset_token: str


class ResetPasswordRequest(CamelModel):
    reset_token: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def valida_senha(cls, v: str) -> str:
        erros = validar_regras_senha(v)
        if erros:
            raise ValueError("Senha inválida, requer: " + ", ".join(erros))
        return v
