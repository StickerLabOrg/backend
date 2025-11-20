import enum

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.session import Base

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

    figurinhas = relationship("Figurinha", back_populates="colecao", cascade="all, delete-orphan")
    albuns = relationship("UsuarioAlbum", back_populates="colecao", cascade="all, delete-orphan")


# ========================
# FIGURINHAS
# ========================


class Figurinha(Base):
    __tablename__ = "figurinhas"

    id = Column(Integer, primary_key=True, index=True)
    colecao_id = Column(Integer, ForeignKey("colecoes.id", ondelete="CASCADE"), nullable=False)

    numero = Column(Integer, nullable=False, index=True)
    nome = Column(String, nullable=False)

    # ex: "Atacante", "Goleiro", "Mascote", "Escudo" etc.
    posicao = Column(String, nullable=True)
    # nome do time (Flamengo, Palmeiras, etc.)
    time = Column(String, nullable=True)

    raridade = Column(Enum(RaridadeEnum), nullable=False)
    imagem_url = Column(String, nullable=True)

    colecao = relationship("Colecao", back_populates="figurinhas")
    usuarios = relationship("UsuarioFigurinha", back_populates="figurinha", cascade="all, delete-orphan")


# ========================
# PACOTES
# ========================


class Pacote(Base):
    __tablename__ = "pacotes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco_moedas = Column(Integer, nullable=False)
    quantidade_figurinhas = Column(Integer, nullable=False)

    # JSON com probabilidades de raridade (ex:
    # {"comum": 0.8, "rara": 0.15, "epica": 0.04, "lendaria": 0.01}
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

    figurinha = relationship("Figurinha", back_populates="usuarios")


# ========================
# ÁLBUM DO USUÁRIO
# ========================


class UsuarioAlbum(Base):
    __tablename__ = "usuario_album"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    colecao_id = Column(Integer, ForeignKey("colecoes.id", ondelete="CASCADE"), nullable=False)

    total_encontradas = Column(Integer, default=0)
    total_completas = Column(Integer, default=0)

    colecao = relationship("Colecao", back_populates="albuns")


# ========================
# PACOTE ABERTO (TEMPORÁRIO)
# ========================


class PacoteAberto(Base):
    __tablename__ = "pacotes_abertos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # lista das figurinhas sorteadas, ex:
    # [{"id": 10, "numero": 10, "nome": "...", "raridade": "comum", "nova": True}, ...]
    conteudo = Column(JSON, nullable=False)
