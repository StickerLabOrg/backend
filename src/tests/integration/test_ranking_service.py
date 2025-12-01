import pytest

BASE = "/ranking"


@pytest.mark.asyncio
async def test_ranking_semanal(async_client, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get(f"{BASE}/semanal", headers=headers)
    assert resp.status_code == 200
    assert "ranking" in resp.json()
