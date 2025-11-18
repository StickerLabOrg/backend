import pytest
from typing import List

from src.partidas import service
from src.partidas.schema import PartidaProxima, PartidaLive, EstatisticasPartida


class DummySettings:
    THESPORTSDB_DEFAULT_LEAGUE_ID = "4328"


# Se precisar, monkeypatch em settings também
def test_listar_proximas_partidas_sem_rodada(monkeypatch):
    # mockar get_ultima_rodada e get_partidas_por_rodada

    def fake_get_ultima_rodada(league_id: str):
        return 10

    def fake_get_partidas_por_rodada(league_id: str, rodada: int, season: str = "2024"):
        return [
            PartidaProxima(
                id_partida="123",
                liga_id=league_id,
                liga_nome="Premier League",
                rodada=str(rodada),
                data="2024-01-01",
                horario="16:00",
                estadio="Stadium",
                status="Not Started",
                time_casa={"id": "1", "nome": "Time A", "escudo": None},
                time_fora={"id": "2", "nome": "Time B", "escudo": None},
            )
        ]

    monkeypatch.setattr(service.repository, "get_ultima_rodada", fake_get_ultima_rodada)
    monkeypatch.setattr(
        service.repository,
        "get_partidas_por_rodada",
        fake_get_partidas_por_rodada,
    )

    partidas = service.listar_proximas_partidas(league_id="4328", limit=5)
    assert len(partidas) == 1
    assert partidas[0].liga_nome == "Premier League"
    assert partidas[0].rodada == "11"  # 10 + 1


def test_listar_partidas_ao_vivo(monkeypatch):
    def fake_fetch_live_matches():
        return [
            {
                "event_id": "100",
                "league_name": "Premier League",
                "round": "12",
                "season": "2024-2025",
                "venue": "Anfield",
                "home_team": "Liverpool",
                "away_team": "Chelsea",
                "home_score": 2,
                "away_score": 1,
                "status": "75'",
                "time": None,
                "home_team_badge": "https://example.com/liv.png",
                "away_team_badge": "https://example.com/che.png",
                "shots_home": 10,
                "shots_away": 4,
                "possession_home": "60%",
                "possession_away": "40%",
                "yellow_cards_home": 1,
                "yellow_cards_away": 2,
                "red_cards_home": 0,
                "red_cards_away": 0,
            }
        ]

    monkeypatch.setattr(service.repository, "fetch_live_matches", fake_fetch_live_matches)

    partidas: List[PartidaLive] = service.listar_partidas_ao_vivo()
    assert len(partidas) == 1

    p = partidas[0]
    assert p.id == "100"
    assert p.time_casa == "Liverpool"
    assert p.time_fora == "Chelsea"
    assert p.placar == "2 - 1"
    assert isinstance(p.estatisticas, EstatisticasPartida)
    assert p.estatisticas.chutes_casa == 10
    assert p.estatisticas.posse_casa == "60%"
