import pytest

BASE = "/palpites"


@pytest.mark.asyncio
async def test_criar_palpite(async_client, token):
    headers = {"Authorization": f"Bearer {token}"}

    palpite = {"partida_id": 1, "palpite_gols_casa": 1, "palpite_gols_visitante": 0}

    resp = await async_client.post(BASE + "/", json=palpite, headers=headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_listar_palpites(async_client, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get(BASE + "/", headers=headers)
    assert resp.status_code == 200
