from typing import Optional

from sqlalchemy.orm import Session

from src.colecao.models import (
    Colecao,
    Figurinha,
    Pacote,
    UsuarioAlbum,
    UsuarioFigurinha,
)

# ===============================
# COLEÇÃO (ÁLBUM)
# ===============================


def get_colecao_ativa(db: Session) -> Optional[Colecao]:
    return db.query(Colecao).filter(Colecao.ativa).first()


def get_colecao_by_id(db: Session, colecao_id: int) -> Optional[Colecao]:
    return db.query(Colecao).filter(Colecao.id == colecao_id).first()


def listar_colecoes(db: Session):
    return db.query(Colecao).all()


# ===============================
# FIGURINHAS
# ===============================


def listar_figurinhas_da_colecao(db: Session, colecao_id: int):
    return db.query(Figurinha).filter(Figurinha.colecao_id == colecao_id).order_by(Figurinha.numero).all()


def get_figurinha_by_id(db: Session, figurinha_id: int) -> Optional[Figurinha]:
    return db.query(Figurinha).filter(Figurinha.id == figurinha_id).first()


def listar_figurinhas_por_raridade(db: Session, raridade):
    return db.query(Figurinha).filter(Figurinha.raridade == raridade).all()


def usuario_possui_figurinha(db: Session, usuario_id: int, figurinha_id: int) -> Optional[UsuarioFigurinha]:
    return (
        db.query(UsuarioFigurinha)
        .filter(
            UsuarioFigurinha.usuario_id == usuario_id,
            UsuarioFigurinha.figurinha_id == figurinha_id,
        )
        .first()
    )


# ===============================
# PACOTES
# ===============================


def listar_pacotes(db: Session):
    return db.query(Pacote).all()


def get_pacote_by_id(db: Session, pacote_id: int) -> Optional[Pacote]:
    return db.query(Pacote).filter(Pacote.id == pacote_id).first()


# ===============================
# USUÁRIO / ÁLBUM
# ===============================


def get_album_usuario(db: Session, usuario_id: int, colecao_id: int) -> Optional[UsuarioAlbum]:
    return (
        db.query(UsuarioAlbum)
        .filter(
            UsuarioAlbum.usuario_id == usuario_id,
            UsuarioAlbum.colecao_id == colecao_id,
        )
        .first()
    )


def criar_album_usuario(db: Session, usuario_id: int, colecao_id: int) -> UsuarioAlbum:
    novo = UsuarioAlbum(
        usuario_id=usuario_id,
        colecao_id=colecao_id,
        total_encontradas=0,
        total_completas=0,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


def atualizar_album_usuario(db: Session, album: UsuarioAlbum, encontradas: int):
    album.total_encontradas = encontradas
    album.total_completas = encontradas
    db.commit()


# ===============================
# FIGURINHAS DO USUÁRIO
# ===============================


def listar_figurinhas_do_usuario(db: Session, usuario_id: int):
    return db.query(UsuarioFigurinha).filter(UsuarioFigurinha.usuario_id == usuario_id).all()


def adicionar_figurinha_ao_usuario(db: Session, usuario_id: int, figurinha_id: int):
    existente = usuario_possui_figurinha(db, usuario_id, figurinha_id)

    if existente:
        existente.quantidade += 1
        db.commit()
        return existente, False  # repetida
    else:
        nova = UsuarioFigurinha(
            usuario_id=usuario_id,
            figurinha_id=figurinha_id,
            quantidade=1,
        )
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova, True  # nova figurinha


def contar_figurinhas_unicas_usuario(db: Session, usuario_id: int) -> int:
    return db.query(UsuarioFigurinha).filter(UsuarioFigurinha.usuario_id == usuario_id).count()


# ===============================
# RESETAR ÁLBUM
# ===============================


def resetar_album(db: Session, usuario_id: int):
    db.query(UsuarioFigurinha).filter(UsuarioFigurinha.usuario_id == usuario_id).delete()

    db.query(UsuarioAlbum).filter(UsuarioAlbum.usuario_id == usuario_id).delete()

    db.commit()


# ===============================
# CRUD COLEÇÃO (ADMIN)
# ===============================


def criar_colecao(db: Session, data):
    colecao = Colecao(
        nome=data.nome,
        descricao=data.descricao,
        ano=data.ano,
        total_figurinhas=data.total_figurinhas,
        ativa=data.ativa,
    )
    db.add(colecao)
    db.commit()
    db.refresh(colecao)
    return colecao


def atualizar_colecao(db: Session, colecao: Colecao, data):
    if data.nome is not None:
        colecao.nome = data.nome
    if data.descricao is not None:
        colecao.descricao = data.descricao
    if data.ano is not None:
        colecao.ano = data.ano
    if data.total_figurinhas is not None:
        colecao.total_figurinhas = data.total_figurinhas
    if data.ativa is not None:
        colecao.ativa = data.ativa

    db.commit()
    db.refresh(colecao)
    return colecao


def deletar_colecao(db: Session, colecao: Colecao):
    db.delete(colecao)
    db.commit()
