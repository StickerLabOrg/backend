from sqlalchemy.orm import Session
from . import model_colecao, schemas_colecao

def get_colecao(db: Session, colecao_id: int):
    return db.query(model_colecao.Colecao).filter(model_colecao.Colecao.id == colecao_id).first()

def get_colecoes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model_colecao.Colecao).offset(skip).limit(limit).all()

def create_colecao(db: Session, colecao: schemas_colecao.ColecaoCreate):
    db_colecao = model_colecao.Colecao(**colecao.model_dump())
    db.add(db_colecao)
    db.commit()
    db.refresh(db_colecao)
    return db_colecao

def update_colecao(db: Session, colecao_id: int, colecao_data: schemas_colecao.ColecaoUpdate):
    db_colecao = get_colecao(db, colecao_id)
    if db_colecao:
        update_data = colecao_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_colecao, key, value)
        db.commit()
        db.refresh(db_colecao)
    return db_colecao

def delete_colecao(db: Session, colecao_id: int):
    db_colecao = get_colecao(db, colecao_id)
    if db_colecao:
        db.delete(db_colecao)
        db.commit()
    return db_colecao