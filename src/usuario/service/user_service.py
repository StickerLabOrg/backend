from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import jwt, JWTError
from passlib.context import CryptContext

from src.config import settings
from src.usuario.repository.user_repository import (
    get_user_by_email,
    create_user,
    get_user_by_id,
    update_user_password,
)
from src.usuario.schema import (
    UserRegister,
    UserResponse,
    PerfilResponse,
)
from src.usuario.models.user import User
from src.palpites.model import Palpite

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------------------------
# HELPERS DE SENHA
# -----------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# -----------------------------
# JWT
# -----------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# -----------------------------
# REGISTRO / LOGIN
# -----------------------------
def register_user(db: Session, data: UserRegister) -> User:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise ValueError("E-mail já cadastrado.")

    hashed = get_password_hash(data.password)
    user = create_user(
        db,
        nome=data.nome,
        email=data.email,
        password_hash=hashed,
        time_do_coracao=data.time_do_coracao,
    )
    return user


def login_user(db: Session, email: str, password: str) -> dict:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Credenciais inválidas.")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------
# PERFIL DO USUÁRIO
# -----------------------------
TOTAL_FIGURINHAS_ALBUM = 250  # ajuste depois conforme seu álbum real


def get_user_profile(db: Session, usuario_id: int) -> Optional[PerfilResponse]:
    user: Optional[User] = get_user_by_id(db, usuario_id)
    if not user:
        return None

    # FIGURINHAS – placeholder por enquanto (0)
    total_figurinhas = 0
    progresso_album = 0.0
    # TODO: integrar com módulo de coleções quando estiver pronto

    # PALPITES
    total_palpites = (
        db.query(Palpite)
        .filter(Palpite.usuario_id == usuario_id)
        .count()
    )

    acertos = (
        db.query(func.count())
        .select_from(Palpite)
        .filter(Palpite.usuario_id == usuario_id, Palpite.acertou == True)
        .scalar()
    ) or 0

    taxa_acerto = (
        round((acertos / total_palpites) * 100, 1) if total_palpites > 0 else 0.0
    )

    return PerfilResponse(
        id=user.id,
        nome=user.nome,
        email=user.email,
        time_do_coracao=user.time_do_coracao,
        total_figurinhas=total_figurinhas,
        progresso_album=progresso_album,
        total_palpites=total_palpites,
        taxa_acerto=taxa_acerto,
        coins=user.coins or 0,
    )


# -----------------------------
# ALTERAR SENHA (logado)
# -----------------------------
def change_password(
    db: Session,
    usuario_id: int,
    senha_atual: str,
    nova_senha: str,
):
    user = get_user_by_id(db, usuario_id)
    if not user:
        raise ValueError("Usuário não encontrado.")

    if not verify_password(senha_atual, user.password_hash):
        raise ValueError("Senha atual incorreta.")

    new_hash = get_password_hash(nova_senha)
    update_user_password(db, usuario_id, new_hash)
    return {"mensagem": "Senha alterada com sucesso."}


# -----------------------------
# ESQUECI A SENHA (reset simplificado)
# -----------------------------
def reset_password_by_email(db: Session, email: str, nova_senha: str):
    """
    Fluxo simplificado para 'Esqueci minha senha'.

    ATENÇÃO: para produção, o ideal é gerar um token de reset
    e enviar um link por e-mail. Aqui fazemos direto para
    simplificar o projeto.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("Usuário não encontrado para este e-mail.")

    new_hash = get_password_hash(nova_senha)
    update_user_password(db, user.id, new_hash)
    return {"mensagem": "Senha redefinida com sucesso."}
