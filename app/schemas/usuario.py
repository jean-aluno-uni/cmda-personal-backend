from app.schemas.common import CamelModel


class UsuarioOut(CamelModel):
    id: int
    nome: str
    email: str

    @classmethod
    def from_model(cls, usuario) -> "UsuarioOut":
        return cls(id=usuario.id, nome=usuario.nome_usuario, email=usuario.email)
