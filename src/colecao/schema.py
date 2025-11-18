from pydantic import BaseModel
from typing import List, Optional
from src.colecao.models import RaridadeEnum


class ColecaoCreate(BaseModel):
    nome: str
    descricao: Optional[str]
    ano: int
    total_figurinhas: int
    ativa: bool = True


class ColecaoUpdate(BaseModel):
    nome: Optional[str]
    descricao: Optional[str]
    ano: Optional[int]
    total_figurinhas: Optional[int]
    ativa: Optional[bool]


# ==========================
# FIGURINHA SORTEADA (NOVO)
# ==========================
class FigurinhaSorteada(BaseModel):
    id: int
    numero: int
    nome: str
    posicao: Optional[str] = None
    time: Optional[str] = None
    raridade: str
    imagem_url: Optional[str] = None
    nova: bool


# ==========================
# RESPOSTA DO PACOTE (NOVA)
# ==========================
class AbrirPacoteResponse(BaseModel):
    pacote_id_temporario: int
    figurinhas: List[FigurinhaSorteada]
    novas: int
    repetidas: int
    raridades: dict
    progresso_atual: float
    moedas_restantes: int



class FigurinhaAlbum(BaseModel):
    id: int
    numero: int
    nome: Optional[str] = None
    posicao: Optional[str] = None
    time: Optional[str] = None
    raridade: Optional[RaridadeEnum] = None
    imagem_url: Optional[str] = None

    possui: bool
    quantidade: int = 0

    class Config:
        orm_mode = True


class AlbumResponse(BaseModel):
    colecao_id: int
    nome_colecao: str
    ano: int
    total_figurinhas: int
    coletadas: int
    progresso: float  # 0.0 a 100.0

    figurinhas: List[FigurinhaAlbum]