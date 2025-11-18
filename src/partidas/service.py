from typing import List, Optional

from src.partidas.schema import (
    PartidaProxima,
    PartidaResultado,
    TabelaTime,
    Liga,
    ElencoResponse,
    TimeInfo,
)
from src.config import settings
from src.partidas import repository
from src.partidas.repository import fetch_live_matches, get_partida_por_id

DEFAULT_LEAGUE_ID = settings.THESPORTSDB_DEFAULT_LEAGUE_ID
DEFAULT_SEASON = settings.THESPORTSDB_DEFAULT_SEASON


# -------------------- LIGAS --------------------

def listar_ligas_por_pais(pais: str) -> List[Liga]:
    return repository.get_ligas_por_pais(pais)


# -------------------- PRÓXIMAS PARTIDAS --------------------

def listar_proximas_partidas(
    league_id: Optional[str] = None,
    limit: int = 10,
) -> List[PartidaProxima]:

    lid = league_id or DEFAULT_LEAGUE_ID
    partidas = repository.get_proximas_partidas_league(lid)
    return partidas[:limit]


# -------------------- ÚLTIMOS RESULTADOS --------------------

def listar_ultimos_resultados(
    league_id: Optional[str] = None,
    limit: int = 10,
) -> List[PartidaResultado]:

    lid = league_id or DEFAULT_LEAGUE_ID
    return repository.get_ultimos_resultados(lid, limit)


# -------------------- TABELA --------------------

def listar_tabela(
    league_id: Optional[str] = None,
    season: Optional[str] = None,
) -> List[TabelaTime]:

    lid = league_id or DEFAULT_LEAGUE_ID
    temporada = season or DEFAULT_SEASON
    return repository.get_tabela(lid, temporada)


# -------------------- ELENCO --------------------

def obter_elenco_time(team_id: str) -> ElencoResponse:
    return repository.get_elenco_time(team_id)


# -------------------- AO VIVO (V2) --------------------

def listar_partidas_ao_vivo(league_id: Optional[str] = None):
    """
    Retorna apenas os jogos ao vivo da liga desejada.
    """
    lid = str(league_id or DEFAULT_LEAGUE_ID)

    eventos = fetch_live_matches()
    partidas = []

    for ev in eventos:

        # Filtra pela liga correta
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


# -------------------- PARTIDA POR ID --------------------

def obter_resultado_partida_por_id(event_id: str) -> Optional[PartidaResultado]:
    return get_partida_por_id(event_id)
