from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config import settings
from src.palpites.model import Palpite
from src.usuario.models.user import User
from src.usuario.repository.user_repository import create_user, get_user_by_email, get_user_by_id, update_user_password
from src.usuario.schema import PerfilResponse, UserRegister

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
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# -----------------------------
# REGISTRO / LOGIN
# -----------------------------
def register_user(db: Session, data: UserRegister) -> User:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise ValueError("E-mail já cadastrado.")

    time = getattr(data, "time_do_coracao", None)

    if not time:
        time = "Sem time"

    hashed = get_password_hash(data.password)

    user = create_user(
        db,
        nome=data.nome,
        email=data.email,
        password_hash=hashed,
        time_do_coracao=time,
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
    user = get_user_by_id(db, usuario_id)
    if not user:
        return None

    # FIGURINHAS (placeholder até integrar com álbum)
    total_figurinhas = 0
    progresso_album = 0.0

    # PALPITES
    total_palpites = db.query(Palpite).filter(Palpite.usuario_id == usuario_id).count()

    acertos = (
        db.query(func.count()).select_from(Palpite).filter(Palpite.usuario_id == usuario_id, Palpite.acertou).scalar()
    ) or 0

    taxa_acerto = round((acertos / total_palpites) * 100, 1) if total_palpites > 0 else 0.0

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

    # CORRIGIDO: antes estava user.senha_hash (campo inexistente)
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
    Fluxo simples para 'Esqueci minha senha'.
    Para produção, recomendável usar token enviado por e-mail.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("Usuário não encontrado para este e-mail.")

    new_hash = get_password_hash(nova_senha)
    update_user_password(db, user.id, new_hash)
    return {"mensagem": "Senha redefinida com sucesso."}
