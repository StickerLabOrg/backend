from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.usuario.schema import (
    UserRegister,
    UserResponse,
    TokenResponse,
    PerfilResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
)
from src.usuario.service.user_service import (
    register_user,
    login_user,
    get_user_profile,
    change_password,
    reset_password_by_email,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# -----------------------------
# REGISTRO
# -----------------------------
@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data)
        return UserResponse(
            id=user.id,
            nome=user.nome,
            email=user.email,
            time_do_coracao=user.time_do_coracao,
            coins=user.coins,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        token_data = login_user(db, form_data.username, form_data.password)
        return token_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# -----------------------------
# PERFIL
# -----------------------------
@router.get("/perfil/{usuario_id}", response_model=PerfilResponse)
def get_perfil(usuario_id: int, db: Session = Depends(get_db)):
    perfil = get_user_profile(db, usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return perfil


# -----------------------------
# ALTERAR SENHA (usuário logado)
# -----------------------------
@router.post("/alterar-senha")
def alterar_senha(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        return change_password(
            db,
            usuario_id=data.usuario_id,
            senha_atual=data.senha_atual,
            nova_senha=data.nova_senha,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -----------------------------
# ESQUECI A SENHA
# -----------------------------
@router.post("/esqueci-senha")
def esqueci_senha(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Fluxo simplificado: o usuário informa o e-mail e a nova senha.
    Em produção, aqui deveria ser um fluxo com token enviado por e-mail.
    """
    try:
        return reset_password_by_email(db, data.email, data.nova_senha)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
