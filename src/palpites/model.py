from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from src.db.session import Base


class Palpite(Base):
    __tablename__ = "palpites"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partida_id = Column(String, nullable=False)  # idEvent da API V2
    palpite = Column(String, nullable=False)

    acertou = Column(Boolean, nullable=True)  # None = não processado
    processado = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
