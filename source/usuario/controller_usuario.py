from sqlalchemy.orm import Session
from . import model_usuario, schemas_usuario
from .. import auth # Importa o auth.py do diretório pai (source)

def get_user_by_email(db: Session, email: str):
    """
    Busca um usuário no banco de dados pelo e-mail.
    """
    return db.query(model_usuario.Usuario).filter(model_usuario.Usuario.email == email).first()

def create_user(db: Session, user: schemas_usuario.UsuarioCreate):
    """
    Cria um novo usuário no banco de dados.
    """
    # Criptografa a senha antes de salvar
    hashed_password = auth.get_password_hash(user.password)
    
    # Cria a instância do modelo SQLAlchemy
    db_user = model_usuario.Usuario(
        email=user.email,
        nome=user.nome,
        time_do_coracao=user.time_do_coracao,
        senha_hash=hashed_password
        # Os valores padrão (moedas, is_admin, etc.) são definidos no model_usuario.py
    )
    
    # Adiciona, commita e atualiza o objeto
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # A linha mais importante: retornar o objeto SQLAlchemy
    # O FastAPI e o Pydantic (com from_attributes=True)
    # farão a conversão para o UsuarioSchema.
    return db_user

