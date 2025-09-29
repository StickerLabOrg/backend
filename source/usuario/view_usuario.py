from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from config import SessionLocal
from . import controller_usuario, schemas_usuario, model_usuario
from .. import auth

# Cria o router ANTES de usá-lo
router = APIRouter()

# Define o schema Token
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/usuarios/", response_model=schemas_usuario.UsuarioSchema, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas_usuario.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = controller_usuario.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já registrado")
    return controller_usuario.create_user(db=db, user=user)

# ... (seu endpoint de depuração /usuarios/all)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ... (resto da função de login)
    user = controller_usuario.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}