from typing import Optional
from pydantic import BaseModel

class PalpiteCreate(BaseModel):
    usuario_id: int
    partida_id: str
    palpite: str

class PalpiteUpdate(BaseModel):
    palpite: str

class PalpiteResponse(BaseModel):
    id: int
    usuario_id: int
    partida_id: str
    palpite: str
    acertou: Optional[bool]
    processado: bool

    class Config:
        orm_mode = True
