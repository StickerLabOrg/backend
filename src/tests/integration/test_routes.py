import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.colecao.models import Colecao, Pacote
from src.usuario.models.user import User


# ============================================================
# FIXTURE — AUTENTICAÇÃO
# ============================================================
@pytest_asyncio.fixture
async def auth_header(async_client: AsyncClient, db: Session):
    """Cria um usuário (se não existir) e retorna o header de autenticação JWT."""

    if db.query(User).filter_by(email="teste@hub.com").first() is None:
        user = User(
            nome="Teste",
            email="teste@hub.com",
            password="123456",
            coins=5000,
        )
        db.add(user)
        db.commit()

    # Login
    response = await async_client.post(
        "/usuarios/login",
        data={"username": "teste@hub.com", "password": "123456"},
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# FIXTURE — CRIAR PACOTE + COLEÇÃO
# ============================================================
@pytest.fixture
def ensure_pacote(db: Session):
    """Garante que exista pelo menos uma coleção e um pacote."""

    if db.query(Colecao).count() == 0:
        col = Colecao(
            nome="Brasileirão 2025",
            ano=2025,
            ativa=True,
            total_figurinhas=200,
        )
        db.add(col)
        db.commit()

    if db.query(Pacote).count() == 0:
        pacote = Pacote(
            nome="Pacote Teste",
            preco_moedas=100,
            quantidade_figurinhas=5,
            chances_raridade={
                "comum": 75,
                "rara": 20,
                "epica": 4,
                "lendaria": 1,
            },
        )
        db.add(pacote)
        db.commit()

    return db.query(Pacote).first()


# ============================================================
# TESTES DE ROTAS GERAIS
# ============================================================

@pytest.mark.asyncio
async def test_criar_usuario(async_client: AsyncClient):
    payload = {
        "email": "novo@hub.com",
        "password": "123456",
        "nome": "Novo Usuário",
    }

    response = await async_client.post("/usuarios/", json=payload)
    assert response.status_code in (200, 201, 409)


@pytest.mark.asyncio
async def test_login(async_client: AsyncClient, auth_header):
    assert "Authorization" in auth_header


@pytest.mark.asyncio
async def test_comprar_pacote(async_client, auth_header, ensure_pacote):
    pacote = ensure_pacote

    response = await async_client.post(
        f"/colecao/comprar/{pacote.id}",
        headers=auth_header,
    )

    assert response.status_code == 200
    assert "figurinhas" in response.json()


@pytest.mark.asyncio
async def test_ver_album(async_client, auth_header):
    response = await async_client.get("/colecao/album", headers=auth_header)

    assert response.status_code == 200
    assert "colecao_id" in response.json()


@pytest.mark.asyncio
async def test_listar_repetidas(async_client, auth_header):
    response = await async_client.get("/colecao/repetidas", headers=auth_header)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_criar_palpite(async_client, auth_header):
    payload = {
        "partida_id": "12345",
        "palpite_gols_casa": 1,
        "palpite_gols_visitante": 0,
    }

    response = await async_client.post(
        "/palpites/",
        json=payload,
        headers=auth_header,
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_ver_ranking(async_client):
    response = await async_client.get("/ranking/")
    assert response.status_code in (200, 404)
