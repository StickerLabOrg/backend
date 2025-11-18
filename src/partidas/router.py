from fastapi import APIRouter, Query
from typing import Optional, List

from src.partidas import service
from src.partidas.schema import (
    Liga,
    PartidaProxima,
    PartidaResultado,
    TabelaTime,
    ElencoResponse,
)

router = APIRouter(prefix="/partidas", tags=["Partidas"])


# -------------------- LIGAS --------------------
@router.get("/ligas", response_model=List[Liga])
def listar_ligas(pais: str = Query(...)):
    return service.listar_ligas_por_pais(pais)


# -------------------- PRÓXIMAS PARTIDAS --------------------
@router.get("/proximas", response_model=List[PartidaProxima])
def proximas_partidas(
    league_id: Optional[str] = None,
    limit: int = 10
):
    return service.listar_proximas_partidas(league_id, limit)


# -------------------- ÚLTIMOS RESULTADOS --------------------
@router.get("/ultimos-resultados", response_model=List[PartidaResultado])
def ultimos_resultados(
    league_id: Optional[str] = None,
    limit: int = 10
):
    return service.listar_ultimos_resultados(league_id, limit)


# -------------------- TABELA --------------------
@router.get("/tabela", response_model=List[TabelaTime])
def tabela(
    league_id: Optional[str] = None,
    season: Optional[str] = None
):
    return service.listar_tabela(league_id, season)


# -------------------- ELENCO --------------------
@router.get("/elenco/{team_id}", response_model=ElencoResponse)
def elenco(team_id: str):
    return service.obter_elenco_time(team_id)


# -------------------- AO VIVO --------------------
@router.get("/ao-vivo")
def ao_vivo(
    league_id: Optional[str] = None
):
    return service.listar_partidas_ao_vivo(league_id)


# -------------------- PARTIDA POR ID --------------------
@router.get("/resultado/{event_id}", response_model=Optional[PartidaResultado])
def resultado_partida(event_id: str):
    return service.obter_resultado_partida_por_id(event_id)

@router.get("/ao_vivo")
def partidas_ao_vivo():
    return service.listar_partidas_ao_vivo()
