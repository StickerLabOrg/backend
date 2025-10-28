from sqlalchemy import Column, Integer, String, Boolean
from config import Base

class Colecao(Base):
    __tablename__ = "colecoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    ano = Column(Integer)
    ativo = Column(Boolean, default=True)