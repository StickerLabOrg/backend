from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.ranking.service import ranking_geral, ranking_mensal, ranking_semanal
from src.ranking.schema import RankingResponse

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/geral", response_model=RankingResponse)
def get_rank_geral(usuario_id: int, db: Session = Depends(get_db)):
    return ranking_geral(db, usuario_id)


@router.get("/mensal", response_model=RankingResponse)
def get_rank_mensal(usuario_id: int, db: Session = Depends(get_db)):
    return ranking_mensal(db, usuario_id)


@router.get("/semanal", response_model=RankingResponse)
def get_rank_semanal(usuario_id: int, db: Session = Depends(get_db)):
    return ranking_semanal(db, usuario_id)
