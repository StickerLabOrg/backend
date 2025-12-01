from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PalpiteCreate(BaseModel):
    partida_id: int
    palpite_gols_casa: int
    palpite_gols_visitante: int


class PalpiteUpdate(BaseModel):
    palpite_gols_casa: Optional[int] = None
    palpite_gols_visitante: Optional[int] = None


class PalpiteResponse(BaseModel):
    id: int
    usuario_id: int
    partida_id: int
    palpite_gols_casa: int
    palpite_gols_visitante: int
    acertou: Optional[bool] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @staticmethod
    def from_model(model):
        gols = model.palpite.replace("-", "x").lower().split("x")
        return PalpiteResponse(
            id=model.id,
            usuario_id=model.usuario_id,
            partida_id=int(model.partida_id),
            palpite_gols_casa=int(gols[0]),
            palpite_gols_visitante=int(gols[1]),
            acertou=model.acertou,
            created_at=model.created_at,
        )
