from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class TimeInfo(BaseModel):
    id: str
    nome: str
    escudo: Optional[HttpUrl] = None


class PartidaBase(BaseModel):
    id_partida: str
    liga_id: str
    liga_nome: Optional[str] = None
    rodada: Optional[str] = None
    data: Optional[str] = None
    horario: Optional[str] = None
    estadio: Optional[str] = None
    status: Optional[str] = None


class PartidaProxima(PartidaBase):
    time_casa: TimeInfo
    time_fora: TimeInfo


class PartidaResultado(PartidaBase):
    time_casa: TimeInfo
    time_fora: TimeInfo
    placar_casa: Optional[int] = None
    placar_fora: Optional[int] = None


class TabelaTime(BaseModel):
    posicao: int
    time_id: str
    time_nome: str
    escudo: Optional[HttpUrl] = None
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_pro: int
    gols_contra: int
    saldo: int


class Liga(BaseModel):
    id: str
    nome: str
    pais: Optional[str] = None
    tipo: Optional[str] = None
    logo: Optional[HttpUrl] = None


class Jogador(BaseModel):
    id: str
    nome: str
    posicao: Optional[str] = None
    numero: Optional[int] = None
    nacionalidade: Optional[str] = None
    foto: Optional[HttpUrl] = None


class ElencoResponse(BaseModel):
    time: TimeInfo
    jogadores: List[Jogador]


class PartidaLive(BaseModel):
    id: str
    time_casa: str
    time_fora: str
    placar: str
    minuto: Optional[str] = None
    escudo_casa: Optional[str] = None
    escudo_fora: Optional[str] = None
