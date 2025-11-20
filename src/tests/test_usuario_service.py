import pytest

BASE = "/usuarios"


@pytest.mark.asyncio
async def test_criar_usuario(async_client):
    data = {"nome": "Lucas", "email": "lucas@test.com", "password": "123", "time_do_coracao": "Palmeiras"}
    resp = await async_client.post(f"{BASE}/", json=data)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_login(async_client):
    data = {"username": "test@example.com", "password": "123"}
    resp = await async_client.post(f"{BASE}/login", data=data)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_get_me(async_client, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get(f"{BASE}/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "test@example.com"
