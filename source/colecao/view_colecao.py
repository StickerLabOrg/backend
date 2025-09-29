from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import SessionLocal
from . import controller_colecao, schemas_colecao

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/colecoes/", response_model=schemas_colecao.ColecaoSchema, status_code=201)
def create_new_colecao(colecao: schemas_colecao.ColecaoCreate, db: Session = Depends(get_db)):
    return controller_colecao.create_colecao(db=db, colecao=colecao)

@router.get("/colecoes/", response_model=List[schemas_colecao.ColecaoSchema])
def read_all_colecoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller_colecao.get_colecoes(db, skip=skip, limit=limit)

# ... (Restante dos endpoints GET(id), PUT, DELETE)