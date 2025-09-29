from sqlalchemy import Column, Integer, String, Boolean, Float
from config import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # AQUI ESTÁ A CORREÇÃO: String(60)
    senha_hash = Column(String(60), nullable=False) 
    is_admin = Column(Boolean, default=False)
    moedas = Column(Integer, default=100)
    time_do_coracao = Column(String)
    pontos = Column(Integer, default=0)
    taxa_de_acerto = Column(Float, default=0.0)