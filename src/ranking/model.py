from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.db.base import Base

class Palpite(Base):
    __tablename__ = "palpites"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    partida_id = Column(String, nullable=False)
    palpite = Column(String, nullable=False)

    acertou = Column(Boolean, nullable=True)
    processado = Column(Boolean, default=False)

    # NECESSÁRIO PARA O RANKING
    created_at = Column(DateTime, server_default=func.now())
