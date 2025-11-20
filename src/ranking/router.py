from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.ranking.schema import RankingResponse
from src.ranking.service import ranking_geral, ranking_mensal, ranking_semanal
from src.usuario.auth import get_current_user

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/geral", response_model=RankingResponse)
def get_rank_geral(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return ranking_geral(db, usuario.id)


@router.get("/mensal", response_model=RankingResponse)
def get_rank_mensal(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return ranking_mensal(db, usuario.id)


@router.get("/semanal", response_model=RankingResponse)
def get_rank_semanal(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return ranking_semanal(db, usuario.id)
