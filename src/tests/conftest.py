import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.session import Base, get_db
from src.main import app
from src.usuario.auth import create_access_token, hash_password
from src.usuario.models.user import User

# =============================================================
# BANCO DE TESTE (SQLite isolado)
# =============================================================
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================
# FIXTURE PRINCIPAL DO BANCO — RESETA E CRIA TABELAS ANTES DE CADA TESTE
# =============================================================
@pytest.fixture()
def db():
    # Drop e create all garantidos ANTES da sessão iniciar
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# =============================================================
# Override do get_db — garante que ROTEADORES usem o DB acima
# =============================================================
@pytest.fixture(autouse=True)
def override_get_db(db):
    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db


# =============================================================
# Cria usuário padrão (ID=1) APÓS o DB existir
# =============================================================
@pytest.fixture(autouse=True)
def create_default_user(db):
    user = User(
        id=1,
        nome="Teste",
        email="test@example.com",
        password_hash=hash_password("123"),
        time_do_coracao="Palmeiras",
        coins=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)


# =============================================================
# CLIENTE HTTP ASSÍNCRONO
# =============================================================
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# =============================================================
# FIXTURE DO TOKEN
# =============================================================
@pytest.fixture
def token():
    return create_access_token({"sub": "1"})
