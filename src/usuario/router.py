from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.usuario.auth import get_current_user

# <-- AGORA IMPORTA!
from src.usuario.schema import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    PerfilResponse,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from src.usuario.service.user_service import (
    change_password,
    get_user_profile,
    login_user,
    register_user,
    reset_password_by_email,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# -----------------------------
# REGISTRO (testes: POST /usuarios/)
# -----------------------------
@router.post("/", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------
# LOGIN (testes enviam JSON)
# -----------------------------
@router.post("/login", response_model=TokenResponse)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        return login_user(db=db, email=username, password=password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# -----------------------------
# PERFIL DO USUÁRIO LOGADO
# -----------------------------
@router.get("/me", response_model=PerfilResponse)
def get_me(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    perfil = get_user_profile(db, usuario.id)
    if not perfil:
        raise HTTPException(404, "Usuário não encontrado")
    return perfil


# -----------------------------
# ALTERAR SENHA (usuário logado)
# -----------------------------
@router.post("/alterar-senha")
def alterar_senha(data: ChangePasswordRequest, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    try:
        return change_password(
            db,
            usuario_id=usuario.id,
            senha_atual=data.senha_atual,
            nova_senha=data.nova_senha,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------
# ESQUECI A SENHA
# -----------------------------
@router.post("/esqueci-senha")
def esqueci_senha(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return reset_password_by_email(db, data.email, data.nova_senha)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
