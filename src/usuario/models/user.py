from sqlalchemy import Column, Integer, String, Boolean
from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    time_do_coracao = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    coins = Column(Integer, default=0)
