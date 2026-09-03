from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, nome_usuario: str, email: str, senha_hash: str, role: str = "motorista") -> Usuario:
        usuario = Usuario(nome_usuario=nome_usuario, email=email, senha_hash=senha_hash, role=role)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update_senha(self, usuario: Usuario, senha_hash: str) -> Usuario:
        usuario.senha_hash = senha_hash
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
