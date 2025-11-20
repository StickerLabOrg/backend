from typing import List, Optional

from src.config import settings
from src.partidas import repository
from src.partidas.repository import fetch_live_matches, get_partida_por_id
from src.partidas.schema import (
    ElencoResponse,
    Liga,
    PartidaProxima,
    PartidaResultado,
    TabelaTime,
)

DEFAULT_LEAGUE_ID = settings.THESPORTSDB_DEFAULT_LEAGUE_ID
DEFAULT_SEASON = settings.THESPORTSDB_DEFAULT_SEASON


# ---------------------------------------------------
# LIGAS
# ---------------------------------------------------


def get_ligas_por_pais(pais: str) -> List[Liga]:
    return repository.get_ligas_por_pais(pais)


# ---------------------------------------------------
# PRÓXIMAS PARTIDAS
# ---------------------------------------------------


def get_proximas_partidas_league(
    league_id: Optional[str] = None,
    limit: int = 10,
) -> List[PartidaProxima]:

    lid = league_id or DEFAULT_LEAGUE_ID
    partidas = repository.get_proximas_partidas_league(lid)
    return partidas[:limit]


# ---------------------------------------------------
# ÚLTIMOS RESULTADOS
# ---------------------------------------------------


def get_ultimos_resultados(
    league_id: Optional[str] = None,
    limit: int = 10,
) -> List[PartidaResultado]:

    lid = league_id or DEFAULT_LEAGUE_ID
    return repository.get_ultimos_resultados(lid, limit)


# ---------------------------------------------------
# TABELA
# ---------------------------------------------------


def get_tabela(
    league_id: Optional[str] = None,
    season: Optional[str] = None,
) -> List[TabelaTime]:

    lid = league_id or DEFAULT_LEAGUE_ID
    temporada = season or DEFAULT_SEASON
    return repository.get_tabela(lid, temporada)


# ---------------------------------------------------
# ELENCO
# ---------------------------------------------------


def get_elenco_time(team_id: str) -> ElencoResponse:
    return repository.get_elenco_time(team_id)


# ---------------------------------------------------
# AO VIVO
# ---------------------------------------------------


def get_partidas_ao_vivo(league_id: Optional[str] = None):
    """
    Retorna somente jogos ao vivo da liga desejada.
    """
    lid = str(league_id or DEFAULT_LEAGUE_ID)

    eventos = fetch_live_matches()
    partidas = []

    for ev in eventos:
        # Filtrar pela liga correta
        if str(ev.get("idLeague")) != lid:
            continue

        partidas.append(
            {
                "idEvent": ev.get("idEvent"),
                "liga": ev.get("strLeague"),
                "time_casa": ev.get("strHomeTeam"),
                "time_fora": ev.get("strAwayTeam"),
                "placar": f"{ev.get('intHomeScore')} - {ev.get('intAwayScore')}",
                "status": ev.get("strStatus"),
                "escudo_casa": ev.get("strHomeTeamBadge"),
                "escudo_fora": ev.get("strAwayTeamBadge"),
            }
        )

    return partidas


# ---------------------------------------------------
# PARTIDA POR ID
# ---------------------------------------------------


def obter_resultado_partida_por_id(event_id: str) -> Optional[PartidaResultado]:
    return get_partida_por_id(event_id)
