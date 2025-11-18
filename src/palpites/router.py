from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.palpites.service import (
    criar_palpite,
    listar_palpites,
    editar_palpite,
    avaliar_palpites_da_partida,
    avaliar_palpites_da_partida_teste,
    processar_palpites_automaticamente
)
from src.palpites.schema import PalpiteCreate, PalpiteResponse, PalpiteUpdate

router = APIRouter(prefix="/palpites", tags=["Palpites"])


@router.post("/", response_model=PalpiteResponse)
def criar_palpite_endpoint(palpite: PalpiteCreate, db: Session = Depends(get_db)):
    return criar_palpite(db, palpite)


@router.get("/", response_model=list[PalpiteResponse])
def listar_palpites_endpoint(db: Session = Depends(get_db)):
    return listar_palpites(db)


@router.put("/{palpite_id}", response_model=PalpiteResponse)
def editar_palpite_endpoint(
    palpite_id: int,
    dados: PalpiteUpdate,
    usuario_id: int,
    db: Session = Depends(get_db),
):
    palpite = editar_palpite(db, palpite_id, dados, usuario_id)
    if not palpite:
        raise HTTPException(404, "Palpite não encontrado ou já processado")
    return palpite


@router.post("/avaliar/{partida_id}", response_model=list[PalpiteResponse])
def avaliar_endpoint(partida_id: str, db: Session = Depends(get_db)):
    r = avaliar_palpites_da_partida(db, partida_id)
    if r is None:
        raise HTTPException(400, "Partida ainda não finalizada ou não encontrada")
    return r


@router.post("/processar-teste")
def processar_teste(data: dict, db: Session = Depends(get_db)):
    return avaliar_palpites_da_partida_teste(
        db, data["partida_id"], data["resultado"]
    )


@router.post("/processar-automatico")
def processar_auto(db: Session = Depends(get_db)):
    return processar_palpites_automaticamente(db)
