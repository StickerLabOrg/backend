from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.palpites.schema import PalpiteCreate, PalpiteResponse, PalpiteUpdate
from src.palpites.service import (
    avaliar_palpites_da_partida,
    avaliar_palpites_da_partida_teste,
    criar_palpite,
    editar_palpite,
    listar_palpites,
    processar_palpites_automaticamente,
)
from src.usuario.auth import get_current_user

router = APIRouter(prefix="/palpites", tags=["Palpites"])


@router.post("/", response_model=PalpiteResponse)
def criar_palpite_endpoint(palpite: PalpiteCreate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return criar_palpite(db, palpite, usuario.id)


@router.get("/", response_model=list[PalpiteResponse])
def listar_palpites_endpoint(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return listar_palpites(db, usuario.id)


@router.put("/{palpite_id}", response_model=PalpiteResponse)
def editar_palpite_endpoint(
    palpite_id: int, dados: PalpiteUpdate, db: Session = Depends(get_db), usuario=Depends(get_current_user)
):
    palpite = editar_palpite(db, palpite_id, dados, usuario.id)
    if not palpite:
        raise HTTPException(404, "Palpite não encontrado ou já processado")
    return palpite


@router.post("/avaliar/{partida_id}", response_model=list[PalpiteResponse])
def avaliar_endpoint(partida_id: str, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    r = avaliar_palpites_da_partida(db, partida_id)
    if r is None:
        raise HTTPException(400, "Partida ainda não finalizada ou não encontrada")
    return r


@router.post("/processar-teste")
def processar_teste(data: dict, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return avaliar_palpites_da_partida_teste(db, data["partida_id"], data["resultado"])


@router.post("/processar-automatico")
def processar_auto(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return processar_palpites_automaticamente(db)
