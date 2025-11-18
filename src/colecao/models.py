from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base
import enum


# ========================
# RARIDADE ENUM
# ========================

class RaridadeEnum(enum.Enum):
    comum = "comum"
    rara = "rara"
    epica = "epica"
    lendaria = "lendaria"


# ========================
# COLEÇÃO (ÁLBUM)
# ========================

class Colecao(Base):
    __tablename__ = "colecoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    ano = Column(Integer, nullable=False)
    total_figurinhas = Column(Integer, nullable=False)
    ativa = Column(Boolean, default=True)

    figurinhas = relationship("Figurinha", back_populates="colecao")


# ========================
# FIGURINHA
# ========================

class Figurinha(Base):
    __tablename__ = "figurinhas"

    id = Column(Integer, primary_key=True, index=True)
    colecao_id = Column(Integer, ForeignKey("colecoes.id", ondelete="CASCADE"), nullable=False)

    numero = Column(Integer, nullable=False)
    nome = Column(String, nullable=False)
    posicao = Column(String, nullable=True)
    time = Column(String, nullable=True)
    imagem_url = Column(String, nullable=True)
    raridade = Column(Enum(RaridadeEnum), nullable=False)

    colecao = relationship("Colecao", back_populates="figurinhas")


# ========================
# TIPO DE PACOTE
# ========================

class Pacote(Base):
    __tablename__ = "pacotes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco_moedas = Column(Integer, nullable=False)
    quantidade_figurinhas = Column(Integer, nullable=False)

    # JSON com probabilidades de raridade
    chances_raridade = Column(JSON, nullable=False)


# ========================
# FIGURINHAS DO USUÁRIO
# ========================

class UsuarioFigurinha(Base):
    __tablename__ = "usuario_figurinhas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    figurinha_id = Column(Integer, ForeignKey("figurinhas.id", ondelete="CASCADE"), nullable=False)

    quantidade = Column(Integer, default=1)


# ========================
# PROGRESSO DO ÁLBUM DO USUÁRIO
# ========================

class UsuarioAlbum(Base):
    __tablename__ = "usuario_album"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    colecao_id = Column(Integer, ForeignKey("colecoes.id", ondelete="CASCADE"), nullable=False)

    total_encontradas = Column(Integer, default=0)
    total_completas = Column(Integer, default=0)

class PacoteAberto(Base):
    __tablename__ = "pacotes_abertos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    conteudo = Column(JSON, nullable=False)  # lista das figurinhas sorteadas
