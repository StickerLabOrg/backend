from typing import Dict, List, Optional

from pydantic import BaseModel

from src.colecao.models import RaridadeEnum

# ========================
# COLEÇÃO (CRUD)
# ========================


class ColecaoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ano: int
    total_figurinhas: int
    ativa: bool = True


class ColecaoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ano: Optional[int] = None
    total_figurinhas: Optional[int] = None
    ativa: Optional[bool] = None


# ========================
# FIGURINHAS
# ========================


class FigurinhaBase(BaseModel):
    id: int
    numero: int
    nome: str
    posicao: Optional[str] = None
    time: Optional[str] = None
    raridade: RaridadeEnum
    imagem_url: Optional[str] = None

    class Config:
        orm_mode = True


class FigurinhaAlbum(BaseModel):
    id: int
    numero: int
    nome: str
    posicao: Optional[str] = None
    time: Optional[str] = None
    raridade: RaridadeEnum
    imagem_url: Optional[str] = None
    possui: bool
    quantidade: int

    class Config:
        orm_mode = True


# ========================
# LOJA DE PACOTES
# ========================


class PacoteResponse(BaseModel):
    id: int
    nome: str
    preco_moedas: int
    quantidade_figurinhas: int

    class Config:
        orm_mode = True


# ========================
# RESPOSTA ABRIR PACOTE
# ========================


class FigurinhaSorteada(BaseModel):
    id: int
    numero: int
    nome: str
    posicao: Optional[str] = None
    time: Optional[str] = None
    raridade: RaridadeEnum
    imagem_url: Optional[str] = None
    nova: bool


class AbrirPacoteResponse(BaseModel):
    pacote_id_temporario: int
    figurinhas: List[FigurinhaSorteada]
    novas: int
    repetidas: int
    raridades: Dict[str, int]
    progresso_atual: float
    moedas_restantes: int


# ========================
# VISÃO COMPLETA DO ÁLBUM
# ========================


class AlbumResponse(BaseModel):
    colecao_id: int
    nome_colecao: str
    ano: int
    total_figurinhas: int
    coletadas: int
    progresso: float
    figurinhas: List[FigurinhaAlbum]
