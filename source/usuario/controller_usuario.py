from sqlalchemy.orm import Session
from . import model_usuario, schemas_usuario
from .. import auth # .. sobe um nível para a pasta 'source'

def get_user_by_email(db: Session, email: str):
    return db.query(model_usuario.Usuario).filter(model_usuario.Usuario.email == email).first()

def create_user(db: Session, user: schemas_usuario.UsuarioCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = model_usuario.Usuario(
        email=user.email,
        nome=user.nome,
        time_do_coracao=user.time_do_coracao,
        senha_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user