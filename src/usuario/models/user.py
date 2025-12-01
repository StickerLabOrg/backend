from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.db.session import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    # 🔥 CAMPO NECESSÁRIO PARA OS TESTES FUNCIONAREM
    time_do_coracao = Column(String, nullable=True)

    coins = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    figurinhas = relationship("UsuarioFigurinha", cascade="all, delete-orphan")
    albuns = relationship("UsuarioAlbum", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        password = kwargs.pop("password", None)
        super().__init__(**kwargs)

        if password:
            self.set_password(password)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)
