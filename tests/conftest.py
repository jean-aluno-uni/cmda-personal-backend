import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.usuario import Usuario
from app.models.veiculo import Veiculo

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _criar_usuario_com_veiculo(db_session, email: str, senha: str, placa: str) -> tuple[Usuario, Veiculo]:
    usuario = Usuario(nome_usuario="Usuário Teste", email=email, senha_hash=hash_password(senha))
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    veiculo = Veiculo(usuario_id=usuario.id, marca="Fiat", modelo="Argo", ano=2022, placa=placa, conectado=True)
    db_session.add(veiculo)
    db_session.commit()
    db_session.refresh(veiculo)
    return usuario, veiculo


@pytest.fixture()
def usuario_autenticado(client, db_session):
    _usuario, veiculo = _criar_usuario_com_veiculo(db_session, "motorista@teste.com", "Senha@123", "AAA0A00")
    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "motorista@teste.com", "senha": "Senha@123"}
    )
    token = login_resp.json()["accessToken"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "veiculo_id": veiculo.id}


@pytest.fixture()
def outro_usuario_com_veiculo(db_session):
    return _criar_usuario_com_veiculo(db_session, "outro@teste.com", "Senha@123", "BBB0B00")
