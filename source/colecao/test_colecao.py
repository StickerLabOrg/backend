import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from config import Base
from source.colecao.view_colecao import get_db

# --- Configuração do Banco de Dados de Teste ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture do Pytest para gerenciar o banco de dados ---
@pytest.fixture(scope="function")
def db_session():
    # Antes de cada teste: cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Depois de cada teste: apaga todas as tabelas
        Base.metadata.drop_all(bind=engine)

# --- Fixture para sobrescrever a dependência do banco de dados ---
@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Limpa o override depois do teste
    app.dependency_overrides.clear()


# --- Testes ---
def test_criar_colecao_sucesso(test_client):
    response = test_client.post(
        "/admin/colecoes/",
        json={"nome": "Copa do Mundo 2026", "ano": 2026, "ativo": True},
    )
    data = response.json()
    assert response.status_code == 201
    assert data["nome"] == "Copa do Mundo 2026"
    assert data["ano"] == 2026
    assert "id" in data

@pytest.mark.skip(reason="Teste de exclusão ainda não implementado.")
def test_deletar_colecao():
    assert False