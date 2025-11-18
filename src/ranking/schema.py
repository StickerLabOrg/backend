from pydantic import BaseModel
from typing import List, Optional


class RankingItem(BaseModel):
    posicao: int
    medalha: Optional[str]
    avatar: str
    nome: str
    pontos: int
    precisao: float
    palpites: int
    is_you: bool

    class Config:
        orm_mode = True


class RankingResponse(BaseModel):
    total: int
    ranking: List[RankingItem]
