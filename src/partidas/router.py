from typing import List, Optional

from fastapi import APIRouter, Query

from src.partidas import service
from src.partidas.schema import (
    ElencoResponse,
    Liga,
    PartidaProxima,
    PartidaResultado,
    TabelaTime,
)

router = APIRouter(prefix="/partidas", tags=["Partidas"])


# -------------------- LIGAS --------------------
@router.get("/ligas", response_model=List[Liga])
def listar_ligas(pais: str = Query(...)):
    return service.get_ligas_por_pais(pais)


# -------------------- PRÓXIMAS PARTIDAS --------------------
@router.get("/proximas", response_model=List[PartidaProxima])
def proximas_partidas(league_id: Optional[str] = None, limit: int = 10):
    return service.get_proximas_partidas_league(league_id)


# -------------------- ÚLTIMOS RESULTADOS --------------------
@router.get("/ultimos-resultados", response_model=List[PartidaResultado])
def ultimos_resultados(league_id: Optional[str] = None, limit: int = 10):
    return service.get_ultimos_resultados(league_id, limit)


# -------------------- TABELA --------------------
@router.get("/tabela", response_model=List[TabelaTime])
def tabela(league_id: Optional[str] = None, season: Optional[str] = None):
    return service.get_tabela(league_id, season)


# -------------------- ELENCO --------------------
@router.get("/elenco/{team_id}", response_model=ElencoResponse)
def elenco(team_id: str):
    return service.get_elenco_time(team_id)


# -------------------- AO VIVO --------------------
@router.get("/ao-vivo")
def ao_vivo():
    return service.get_partidas_ao_vivo()


# -------------------- PARTIDA POR ID --------------------
@router.get("/resultado/{event_id}", response_model=Optional[PartidaResultado])
def resultado_partida(event_id: str):
    return service.get_partida_por_id(event_id)
