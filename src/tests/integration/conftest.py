import pytest
from httpx import AsyncClient
from src.main import app

@pytest.fixture
def fake_user():
    return {
        "id": 1,
        "nome": "Usuário Teste",
        "email": "teste@hub.com",
        "time_do_coracao": "Flamengo"
    }

@pytest.fixture
async def async_client(monkeypatch, fake_user):
    from src.auth import auth_client

    # Mock do get_current_user
    monkeypatch.setattr(auth_client, "get_current_user", lambda *args, **kwargs: fake_user)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
