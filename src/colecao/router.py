from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.colecao.models import Figurinha, RaridadeEnum, UsuarioFigurinha
from src.colecao.repository import (
    atualizar_colecao,
    criar_colecao,
    deletar_colecao,
    get_colecao_ativa,
    get_colecao_by_id,
    listar_figurinhas_do_usuario,
    listar_pacotes,
    resetar_album,
)
from src.colecao.schema import (
    AbrirPacoteResponse,
    AlbumResponse,
    ColecaoCreate,
    ColecaoUpdate,
    FigurinhaAlbum,
    FigurinhaBase,
    PacoteResponse,
)
from src.colecao.service import (
    abrir_pacote,
    confirmar_insercao,
    montar_album_usuario,
)
from src.db.session import get_db
from src.usuario.auth import get_current_user

router = APIRouter(prefix="/colecao", tags=["Coleção"])


# ===============================
# LOJA DE PACOTES
# ===============================


@router.get("/pacotes", response_model=List[PacoteResponse])
def listar_todos_pacotes(db: Session = Depends(get_db)):
    return listar_pacotes(db)


@router.post("/comprar/{pacote_id}", response_model=AbrirPacoteResponse)
def comprar_pacote(
    pacote_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    try:
        return abrir_pacote(db, usuario, pacote_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pacote/abrir", response_model=AbrirPacoteResponse)
def abrir_pacote_route(
    pacote_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    """
    Endpoint alternativo (usado se você quiser chamar com query param ?pacote_id=1).
    Internamente faz a mesma coisa que /comprar/{pacote_id}.
    """
    try:
        return abrir_pacote(db, usuario, pacote_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pacote/confirmar")
def confirmar_pacote_route(
    pacote_temp_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    try:
        return confirmar_insercao(db, usuario, pacote_temp_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# MINHAS FIGURINHAS
# ===============================


@router.get("/minhas-figurinhas")
def minhas_figurinhas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    return listar_figurinhas_do_usuario(db, usuario.id)


# ===============================
# VISÃO COMPLETA DO ÁLBUM
# ===============================


@router.get("/album", response_model=AlbumResponse)
def ver_album(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    return montar_album_usuario(db, usuario)


@router.post("/album/resetar")
def resetar_album_route(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    resetar_album(db, usuario.id)
    return {"message": "Álbum resetado com sucesso!"}


# ===============================
# CRUD ÁLBUM/COLEÇÃO (ADMIN)
# ===============================


@router.post("/album/criar")
def criar_album_route(
    data: ColecaoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem criar álbuns.")
    return criar_colecao(db, data)


@router.put("/album/{colecao_id}")
def atualizar_album_route(
    colecao_id: int,
    data: ColecaoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem alterar álbuns.")

    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise HTTPException(status_code=404, detail="Álbum não encontrado")

    return atualizar_colecao(db, colecao, data)


@router.delete("/album/{colecao_id}")
def deletar_album_route(
    colecao_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem deletar álbuns.")

    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise HTTPException(status_code=404, detail="Álbum não encontrado")

    deletar_colecao(db, colecao)
    return {"message": "Álbum deletado com sucesso!"}


# ===============================
# FIGURINHAS REPETIDAS
# ===============================


@router.get("/repetidas", response_model=List[FigurinhaAlbum])
def listar_repetidas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    repetidas = (
        db.query(UsuarioFigurinha)
        .filter(
            UsuarioFigurinha.usuario_id == usuario.id,
            UsuarioFigurinha.quantidade > 1,
        )
        .all()
    )

    response: List[FigurinhaAlbum] = []

    for item in repetidas:
        fig = item.figurinha
        response.append(
            FigurinhaAlbum(
                id=fig.id,
                numero=fig.numero,
                nome=fig.nome,
                posicao=fig.posicao,
                time=fig.time,
                raridade=fig.raridade,
                imagem_url=fig.imagem_url,
                possui=True,
                quantidade=item.quantidade,
            )
        )

    return response


@router.get("/repetidas/quantidade")
def quantidade_repetidas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    total = (
        db.query(UsuarioFigurinha)
        .filter(
            UsuarioFigurinha.usuario_id == usuario.id,
            UsuarioFigurinha.quantidade > 1,
        )
        .count()
    )

    return {"total_repetidas": total}


# ===============================
# BUSCA / FIGURINHAS
# ===============================


@router.get("/figurinha/{figurinha_id}", response_model=FigurinhaBase)
def obter_figurinha(
    figurinha_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    fig = db.query(Figurinha).filter(Figurinha.id == figurinha_id).first()
    if not fig:
        raise HTTPException(status_code=404, detail="Figurinha não encontrada")
    return fig


@router.get("/buscar", response_model=List[FigurinhaBase])
def buscar_figurinhas(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    """
    Busca por nome, time ou número da figurinha.
    """
    query = q.strip()
    base = db.query(Figurinha)

    # se for número, busca direto pelo número
    if query.isdigit():
        figs = base.filter(Figurinha.numero == int(query)).all()
    else:
        q_lower = query.lower()
        figs = base.filter(
            or_(
                func.lower(Figurinha.nome).like(f"%{q_lower}%"),
                func.lower(Figurinha.time).like(f"%{q_lower}%"),
            )
        ).all()

    return figs


# ===============================
# FIGURINHAS ESPECIAIS
# ===============================


@router.get("/especiais", response_model=List[FigurinhaBase])
def listar_especiais(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    """
    Retorna apenas figurinhas especiais (rara, épica, lendária).

    Aqui estava o problema antes: comparar string com Enum.
    Agora filtramos usando o Enum corretamente.
    """
    colecao = get_colecao_ativa(db)
    if not colecao:
        return []

    figs = (
        db.query(Figurinha)
        .filter(
            Figurinha.colecao_id == colecao.id,
            Figurinha.raridade.in_([RaridadeEnum.rara, RaridadeEnum.epica, RaridadeEnum.lendaria]),
        )
        .order_by(Figurinha.numero)
        .all()
    )

    return figs
