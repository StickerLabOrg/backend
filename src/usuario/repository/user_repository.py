from sqlalchemy.orm import Session

from src.usuario.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    nome: str,
    email: str,
    password_hash: str,
    time_do_coracao: str,
):
    user = User(
        nome=nome,
        email=email,
        password_hash=password_hash,
        time_do_coracao=time_do_coracao,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, new_password_hash: str):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    return user
