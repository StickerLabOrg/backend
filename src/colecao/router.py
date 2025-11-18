from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.usuario.auth import get_current_user

# SERVICES
from src.colecao.service import (
    abrir_pacote,
    confirmar_insercao,
    montar_album_usuario
)

# SCHEMAS
from src.colecao.schema import (
    AbrirPacoteResponse,
    AlbumResponse,
    ColecaoCreate,
    ColecaoUpdate
)

# MODELS
from src.colecao.models import UsuarioFigurinha

# REPOSITORY
from src.colecao.repository import (
    listar_pacotes,
    listar_figurinhas_do_usuario,
    listar_figurinhas_da_colecao,
    resetar_album,
    get_colecao_ativa,
    get_colecao_by_id,
    criar_colecao,
    atualizar_colecao,
    deletar_colecao
)

from sqlalchemy import func, String
from src.colecao.models import Figurinha


router = APIRouter(prefix="/colecao", tags=["Coleção"])


# ===============================
# LOJA DE PACOTES
# ===============================
@router.get("/pacotes")
def listar_todos_pacotes(db: Session = Depends(get_db)):
    return listar_pacotes(db)


# ===============================
# ABRIR PACOTE
# ===============================
@router.post("/pacote/abrir", response_model=AbrirPacoteResponse)
def abrir_pacote_route(
    pacote_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return abrir_pacote(db, usuario, pacote_id)


# ===============================
# CONFIRMAR INSERÇÃO
# ===============================
@router.post("/pacote/confirmar")
def confirmar_pacote_route(
    pacote_temp_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return confirmar_insercao(db, usuario, pacote_temp_id)


# ===============================
# MINHAS FIGURINHAS
# ===============================
@router.get("/minhas-figurinhas")
def minhas_figurinhas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return listar_figurinhas_do_usuario(db, usuario.id)


# ===============================
# ÁLBUM COMPLETO (Protótipo)
# ===============================
@router.get("/album", response_model=AlbumResponse)
def ver_album(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return montar_album_usuario(db, usuario)


# ===============================
# REPETIDAS
# ===============================
@router.get("/repetidas")
def listar_repetidas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    repetidas = db.query(UsuarioFigurinha).filter(
        UsuarioFigurinha.usuario_id == usuario.id,
        UsuarioFigurinha.quantidade > 1
    ).all()

    return [
        {
            "id": uf.figurinha.id,
            "numero": uf.figurinha.numero,
            "nome": uf.figurinha.nome,
            "time": uf.figurinha.time,
            "raridade": uf.figurinha.raridade.value,
            "imagem_url": uf.figurinha.imagem_url,
            "quantidade": uf.quantidade
        }
        for uf in repetidas
    ]


@router.get("/repetidas/quantidade")
def quantidade_repetidas(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    total = db.query(UsuarioFigurinha).filter(
        UsuarioFigurinha.usuario_id == usuario.id,
        UsuarioFigurinha.quantidade > 1
    ).count()

    return {"total_repetidas": total}


# ===============================
# RESETAR ÁLBUM
# ===============================
@router.post("/album/resetar")
def resetar_album_route(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    resetar_album(db, usuario.id)
    return {"message": "Álbum resetado com sucesso!"}


# ===============================
# ADMIN – CRIAR COLEÇÃO
# ===============================
@router.post("/album/criar")
def criar_album_route(
    data: ColecaoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem criar álbuns.")

    return criar_colecao(db, data)


# ===============================
# ADMIN – ALTERAR COLEÇÃO
# ===============================
@router.put("/album/{colecao_id}")
def atualizar_album_route(
    colecao_id: int,
    data: ColecaoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem alterar álbuns.")

    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise HTTPException(status_code=404, detail="Álbum não encontrado")

    return atualizar_colecao(db, colecao, data)


# ===============================
# ADMIN – DELETAR COLEÇÃO
# ===============================
@router.delete("/album/{colecao_id}")
def deletar_album_route(
    colecao_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas admins podem deletar álbuns.")

    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise HTTPException(status_code=404, detail="Álbum não encontrado")

    deletar_colecao(db, colecao)
    return {"message": "Álbum deletado com sucesso!"}

@router.get("/figurinha/{figurinha_id}")
def detalhes_figurinha(
    figurinha_id: int,
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):
    # Buscar figurinha
    fig = db.query(Figurinha).filter(Figurinha.id == figurinha_id).first()

    if not fig:
        raise HTTPException(status_code=404, detail="Figurinha não encontrada")

    # Verificar se o usuário possui
    registro = db.query(UsuarioFigurinha).filter(
        UsuarioFigurinha.usuario_id == usuario.id,
        UsuarioFigurinha.figurinha_id == fig.id
    ).first()

    possui = registro is not None
    quantidade = registro.quantidade if registro else 0

    return {
        "id": fig.id,
        "numero": fig.numero,
        "nome": fig.nome,
        "posicao": fig.posicao,
        "time": fig.time,
        "raridade": fig.raridade.value,
        "imagem_url": fig.imagem_url,
        "possui": possui,
        "quantidade": quantidade
    }


@router.get("/buscar")
def buscar_figurinhas(
    query: str,
    db: Session = Depends(get_db)
):
    query_lower = query.lower()

    resultados = db.query(Figurinha).filter(
        (func.lower(Figurinha.nome).like(f"%{query_lower}%")) |
        (func.lower(Figurinha.time).like(f"%{query_lower}%")) |
        (func.cast(Figurinha.numero, String).like(f"%{query_lower}%"))
    ).all()

    return [
        {
            "id": f.id,
            "numero": f.numero,
            "nome": f.nome,
            "time": f.time,
            "raridade": f.raridade.value,
            "imagem_url": f.imagem_url
        }
        for f in resultados
    ]

@router.get("/especiais")
def listar_especiais(
    db: Session = Depends(get_db)
):
    especiais = db.query(Figurinha).filter(
        Figurinha.raridade.in_(["rara", "epica", "lendaria"])
    ).order_by(Figurinha.numero).all()

    return [
        {
            "id": f.id,
            "numero": f.numero,
            "nome": f.nome,
            "time": f.time,
            "raridade": f.raridade.value,
            "imagem_url": f.imagem_url
        }
        for f in especiais
    ]

@router.get("/especiais")
def listar_especiais(
    db: Session = Depends(get_db)
):
    especiais = db.query(Figurinha).filter(
        Figurinha.raridade.in_(["rara", "epica", "lendaria"])
    ).order_by(Figurinha.numero).all()

    return [
        {
            "id": f.id,
            "numero": f.numero,
            "nome": f.nome,
            "time": f.time,
            "raridade": f.raridade.value,
            "imagem_url": f.imagem_url
        }
        for f in especiais
    ]
@router.get("/especiais")
def listar_especiais(
    db: Session = Depends(get_db)
):
    especiais = db.query(Figurinha).filter(
        Figurinha.raridade.in_(["rara", "epica", "lendaria"])
    ).order_by(Figurinha.numero).all()

    return [
        {
            "id": f.id,
            "numero": f.numero,
            "nome": f.nome,
            "time": f.time,
            "raridade": f.raridade.value,
            "imagem_url": f.imagem_url
        }
        for f in especiais
    ]

@router.get("/especiais")
def listar_especiais(
    db: Session = Depends(get_db)
):
    especiais = db.query(Figurinha).filter(
        Figurinha.raridade.in_(["rara", "epica", "lendaria"])
    ).order_by(Figurinha.numero).all()

    return [
        {
            "id": f.id,
            "numero": f.numero,
            "nome": f.nome,
            "time": f.time,
            "raridade": f.raridade.value,
            "imagem_url": f.imagem_url
        }
        for f in especiais
    ]
