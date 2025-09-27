from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Importa de 3 lugares diferentes agora, sem ciclo
from . import controller_colecao
from . import schemas_colecao
from config import SessionLocal

# --- Funções de Dependência ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Rotas da API ---
router = APIRouter()

@router.post("/colecoes/", response_model=schemas_colecao.ColecaoSchema, status_code=201)
def create_new_colecao(colecao: schemas_colecao.ColecaoCreate, db: Session = Depends(get_db)):
    return controller_colecao.create_colecao(db=db, colecao=colecao)

@router.get("/colecoes/", response_model=List[schemas_colecao.ColecaoSchema])
def read_all_colecoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    colecoes = controller_colecao.get_colecoes(db, skip=skip, limit=limit)
    return colecoes

@router.get("/colecoes/{colecao_id}", response_model=schemas_colecao.ColecaoSchema)
def read_one_colecao(colecao_id: int, db: Session = Depends(get_db)):
    db_colecao = controller_colecao.get_colecao(db, colecao_id=colecao_id)
    if db_colecao is None:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    return db_colecao

@router.put("/colecoes/{colecao_id}", response_model=schemas_colecao.ColecaoSchema)
def update_existing_colecao(colecao_id: int, colecao: schemas_colecao.ColecaoUpdate, db: Session = Depends(get_db)):
    db_colecao = controller_colecao.update_colecao(db, colecao_id, colecao)
    if db_colecao is None:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    return db_colecao

@router.delete("/colecoes/{colecao_id}", response_model=schemas_colecao.ColecaoSchema)
def delete_existing_colecao(colecao_id: int, db: Session = Depends(get_db)):
    db_colecao = controller_colecao.delete_colecao(db, colecao_id)
    if db_colecao is None:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    return db_colecao