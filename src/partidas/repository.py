import requests
from typing import List, Optional

from src.config import settings
from src.partidas.schema import (
    Liga, PartidaProxima, PartidaResultado, TabelaTime,
    TimeInfo, Jogador, ElencoResponse
)

# BASES
V1_BASE_URL = "https://www.thesportsdb.com/api/v1/json"
V2_BASE_URL = "https://www.thesportsdb.com/api/v2/json"

API_KEY = settings.THESPORTSDB_API_KEY


# -------------------- GENÉRICOS --------------------

def _get_v2(path: str, params: dict = None):
    """Chamada genérica da V2. Header obrigatório."""
    if params is None:
        params = {}

    url = f"{V2_BASE_URL}/{path.lstrip('/')}"
    headers = {"X-API-KEY": API_KEY}

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _get_v1(endpoint: str, params: dict = None):
    """Chamada da V1 (usa key na URL)."""
    if params is None:
        params = {}

    url = f"{V1_BASE_URL}/{API_KEY}/{endpoint}"
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


# -------------------- LIGAS (V1) --------------------

def get_ligas_por_pais(pais: str) -> List[Liga]:
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/search_all_leagues.php"
    resp = requests.get(url, params={"c": pais, "s": "Soccer"}, timeout=15)
    resp.raise_for_status()

    leagues = resp.json().get("countries") or []

    return [
        Liga(
            id=str(lg.get("idLeague")),
            nome=lg.get("strLeague"),
            pais=lg.get("strCountry"),
            tipo=lg.get("strSport"),
            logo=lg.get("strBadge"),
        )
        for lg in leagues
    ]


# -------------------- PRÓXIMAS PARTIDAS (V2 + fallback V1) --------------------

def get_proximas_partidas_league(league_id: str) -> List[PartidaProxima]:
    """
    Tenta buscar próximas partidas pela API V2.
    Se a V2 não retornar nada (lista vazia), faz fallback para V1.
    """
    # --- 1) Tenta V2 ---
    try:
        data_v2 = _get_v2(f"schedule/next/league/{league_id}")
        events_v2 = data_v2.get("events") or []
    except Exception:
        events_v2 = []

    # Se a V2 retornar jogos, usa ela
    if events_v2:
        events = events_v2
    else:
        # --- 2) Fallback para V1 ---
        try:
            data_v1 = _get_v1("eventsnextleague.php", {"id": league_id})
            events = data_v1.get("events") or []
        except Exception:
            events = []

    # --- 3) Mapear eventos para o schema ---
    return [
        PartidaProxima(
            id_partida=str(ev.get("idEvent")),
            liga_id=str(ev.get("idLeague")),
            liga_nome=ev.get("strLeague"),
            rodada=ev.get("intRound"),
            data=ev.get("dateEvent"),
            horario=ev.get("strTime"),   # <--- CORRIGIDO
            estadio=ev.get("strVenue"),
            status=ev.get("strStatus"),
            time_casa=TimeInfo(
                id=str(ev.get("idHomeTeam")),
                nome=ev.get("strHomeTeam"),
                escudo=ev.get("strHomeTeamBadge"),
            ),
            time_fora=TimeInfo(
                id=str(ev.get("idAwayTeam")),
                nome=ev.get("strAwayTeam"),
                escudo=ev.get("strAwayTeamBadge"),
            ),
        )
        for ev in events
    ]


# -------------------- RESULTADOS (V2) --------------------

def get_ultimos_resultados(league_id: str, limit: int = 10) -> List[PartidaResultado]:
    """
    Tenta buscar os últimos resultados pela API V2.
    Se não houver nada, faz fallback para a API V1.
    """
    # --- 1) Tenta V2 ---
    try:
        data_v2 = _get_v2(f"schedule/previous/league/{league_id}")
        events_v2 = data_v2.get("events") or []
    except Exception:
        events_v2 = []

    # Se a V2 retornar algo, usa
    if events_v2:
        events = events_v2[:limit]
    else:
        # --- 2) Fallback para V1 ---
        try:
            data_v1 = _get_v1("eventspastleague.php", {"id": league_id})
            events = (data_v1.get("events") or [])[:limit]
        except Exception:
            events = []

    # --- 3) Mapear para o esquema ---
    return [
        PartidaResultado(
            id_partida=str(ev.get("idEvent")),
            liga_id=str(ev.get("idLeague")),
            liga_nome=ev.get("strLeague"),
            rodada=ev.get("intRound"),
            data=ev.get("dateEvent"),
            horario=ev.get("strTime"),
            estadio=ev.get("strVenue"),
            status=ev.get("strStatus"),
            time_casa=TimeInfo(
                id=str(ev.get("idHomeTeam")),
                nome=ev.get("strHomeTeam"),
                escudo=ev.get("strHomeTeamBadge"),
            ),
            time_fora=TimeInfo(
                id=str(ev.get("idAwayTeam")),
                nome=ev.get("strAwayTeam"),
                escudo=ev.get("strAwayTeamBadge"),
            ),
            placar_casa=int(ev["intHomeScore"]) if ev.get("intHomeScore") else None,
            placar_fora=int(ev["intAwayScore"]) if ev.get("intAwayScore") else None,
        )
        for ev in events
    ]


# -------------------- AO VIVO (V2) --------------------

def fetch_live_matches():
    """Retorna todas as partidas ao vivo."""
    data = _get_v2("livescore/soccer")
    return data.get("events") or data.get("livescore") or []


def get_partidas_ao_vivo():
    return fetch_live_matches()


# -------------------- TABELA (V1) --------------------

def get_tabela(league_id: str, season: Optional[str]):
    params = {"l": league_id, "s": season}
    data = _get_v1("lookuptable.php", params)
    table = data.get("table") or []

    return [
        TabelaTime(
            posicao=int(row.get("intRank") or 0),
            time_id=str(row.get("idTeam")),
            time_nome=row.get("strTeam"),
            escudo=row.get("strTeamBadge"),
            pontos=int(row.get("intPoints") or 0),
            jogos=int(row.get("intPlayed") or 0),
            vitorias=int(row.get("intWin") or 0),
            empates=int(row.get("intDraw") or 0),
            derrotas=int(row.get("intLoss") or 0),
            gols_pro=int(row.get("intGoalsFor") or 0),
            gols_contra=int(row.get("intGoalsAgainst") or 0),
            saldo=int(row.get("intGoalDifference") or 0),
        )
        for row in table
    ]


# -------------------- ELENCO (V2) --------------------

def get_elenco_time(team_id: str) -> ElencoResponse:
    data = _get_v2(f"list/players/{team_id}")
    players = data.get("players") or []

    time_info = TimeInfo(
        id=team_id,
        nome=players[0].get("strTeam") if players else "",
        escudo=players[0].get("strCutout") or players[0].get("strTeamBadge") if players else None,
    )

    return ElencoResponse(
        time=time_info,
        jogadores=[
            Jogador(
                id=str(p.get("idPlayer")),
                nome=p.get("strPlayer"),
                posicao=p.get("strPosition"),
                numero=int(p["strNumber"]) if p.get("strNumber") and str(p["strNumber"]).isdigit() else None,
                nacionalidade=p.get("strNationality"),
                foto=p.get("strCutout") or p.get("strThumb"),
            )
            for p in players
        ],
    )


# -------------------- PARTIDA POR ID (V2) --------------------

def get_partida_por_id(event_id: str):
    data = _get_v2(f"lookup/event/{event_id}")
    events = data.get("lookup") or data.get("events") or []

    if not events:
        return None

    ev = events[0]

    return PartidaResultado(
        id_partida=str(ev.get("idEvent")),
        liga_id=str(ev.get("idLeague")),
        liga_nome=ev.get("strLeague"),
        rodada=ev.get("intRound"),
        data=ev.get("dateEvent"),
        horario=ev.get("strTime"),
        estadio=ev.get("strVenue"),
        status=ev.get("strStatus"),
        time_casa=TimeInfo(
            id=str(ev.get("idHomeTeam")),
            nome=ev.get("strHomeTeam"),
            escudo=ev.get("strHomeTeamBadge"),
        ),
        time_fora=TimeInfo(
            id=str(ev.get("idAwayTeam")),
            nome=ev.get("strAwayTeam"),
            escudo=ev.get("strAwayTeamBadge"),
        ),
        placar_casa=int(ev["intHomeScore"]) if ev.get("intHomeScore") else None,
        placar_fora=int(ev["intAwayScore"]) if ev.get("intAwayScore") else None,
    )
