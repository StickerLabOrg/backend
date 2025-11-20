import random

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.colecao.models import (
    Colecao,
    Figurinha,
    Pacote,
    PacoteAberto,
    RaridadeEnum,
    UsuarioAlbum,
    UsuarioFigurinha,
)
from src.colecao.repository import (
    get_colecao_ativa,
    listar_figurinhas_da_colecao,
    listar_figurinhas_do_usuario,
)
from src.colecao.schema import (
    AlbumResponse,
    FigurinhaAlbum,
)


# ===================================================
# Sorteio baseado nas chances do pacote
# ===================================================
def sortear_raridade(chances: dict) -> str:
    raridades = list(chances.keys())
    pesos = list(chances.values())
    return random.choices(raridades, weights=pesos, k=1)[0]


# ===================================================
# Abrir pacote (pré-visualização)
# ===================================================
def abrir_pacote(db: Session, usuario, pacote_id: int):
    pacote = db.query(Pacote).filter(Pacote.id == pacote_id).first()

    if not pacote:
        raise ValueError("Pacote não encontrado")

    if usuario.coins < pacote.preco_moedas:
        raise ValueError("Moedas insuficientes")

    usuario.coins -= pacote.preco_moedas

    colecao = get_colecao_ativa(db)
    if not colecao:
        raise ValueError("Nenhuma coleção ativa encontrada")

    figurinhas = []
    raridades_contagem = {"comum": 0, "rara": 0, "epica": 0, "lendaria": 0}
    novas = 0
    repetidas = 0

    for _ in range(pacote.quantidade_figurinhas):
        raridade_str = sortear_raridade(pacote.chances_raridade)
        raridade_enum = RaridadeEnum(raridade_str)

        fig = (
            db.query(Figurinha)
            .filter(
                Figurinha.raridade == raridade_enum,
                Figurinha.colecao_id == colecao.id,
            )
            .order_by(func.random())
            .first()
        )

        if not fig:
            continue

        record = (
            db.query(UsuarioFigurinha)
            .filter(
                UsuarioFigurinha.usuario_id == usuario.id,
                UsuarioFigurinha.figurinha_id == fig.id,
            )
            .first()
        )

        is_new = record is None
        if is_new:
            novas += 1
        else:
            repetidas += 1

        raridades_contagem[fig.raridade.value] += 1

        figurinhas.append(
            {
                "id": fig.id,
                "numero": fig.numero,
                "nome": fig.nome,
                "time": fig.time or "",
                "posicao": fig.posicao or "",
                "raridade": fig.raridade.value,
                "imagem_url": fig.imagem_url or "",
                "nova": is_new,
            }
        )

    pacote_temp = PacoteAberto(
        usuario_id=usuario.id,
        conteudo=figurinhas,
    )
    db.add(pacote_temp)
    db.commit()
    db.refresh(pacote_temp)

    progresso = calcular_progresso(db, usuario)

    return {
        "pacote_id_temporario": pacote_temp.id,
        "figurinhas": figurinhas,
        "novas": novas,
        "repetidas": repetidas,
        "raridades": raridades_contagem,
        "progresso_atual": progresso,
        "moedas_restantes": usuario.coins,
    }


# ===================================================
# Progresso do álbum
# ===================================================
def atualizar_progresso_album(db: Session, usuario):
    colecao = db.query(Colecao).filter(Colecao.ativa).first()
    if not colecao:
        return

    figurinhas_unicas = db.query(UsuarioFigurinha).filter(UsuarioFigurinha.usuario_id == usuario.id).count()

    album = (
        db.query(UsuarioAlbum)
        .filter(
            UsuarioAlbum.usuario_id == usuario.id,
            UsuarioAlbum.colecao_id == colecao.id,
        )
        .first()
    )

    if not album:
        album = UsuarioAlbum(
            usuario_id=usuario.id,
            colecao_id=colecao.id,
        )
        db.add(album)

    album.total_completas = figurinhas_unicas
    album.total_encontradas = figurinhas_unicas
    db.commit()


def calcular_progresso(db: Session, usuario) -> float:
    colecao = db.query(Colecao).filter(Colecao.ativa).first()
    if not colecao:
        return 0.0

    album = (
        db.query(UsuarioAlbum)
        .filter(
            UsuarioAlbum.usuario_id == usuario.id,
            UsuarioAlbum.colecao_id == colecao.id,
        )
        .first()
    )

    if not album or colecao.total_figurinhas == 0:
        return 0.0

    progresso = (album.total_completas / colecao.total_figurinhas) * 100
    return round(progresso, 2)


# ===================================================
# Confirmar inserção das figurinhas
# ===================================================
def confirmar_insercao(db: Session, usuario, pacote_temp_id: int):
    pacote_temp = (
        db.query(PacoteAberto)
        .filter(
            PacoteAberto.id == pacote_temp_id,
            PacoteAberto.usuario_id == usuario.id,
        )
        .first()
    )

    if not pacote_temp:
        raise ValueError("Pacote temporário não encontrado")

    colecao = get_colecao_ativa(db)
    conteudo = pacote_temp.conteudo

    novas = 0
    repetidas = 0

    for item in conteudo:
        fig_db = db.query(Figurinha).filter(Figurinha.id == item["id"]).first()
        if not fig_db or fig_db.colecao_id != colecao.id:
            continue

        record = (
            db.query(UsuarioFigurinha)
            .filter(
                UsuarioFigurinha.usuario_id == usuario.id,
                UsuarioFigurinha.figurinha_id == fig_db.id,
            )
            .first()
        )

        if record:
            record.quantidade += 1
            repetidas += 1
        else:
            nova = UsuarioFigurinha(
                usuario_id=usuario.id,
                figurinha_id=fig_db.id,
                quantidade=1,
            )
            db.add(nova)
            novas += 1

    atualizar_progresso_album(db, usuario)

    db.delete(pacote_temp)
    db.commit()

    return {
        "novas_adicionadas": novas,
        "repetidas_incrementadas": repetidas,
        "progresso_final": calcular_progresso(db, usuario),
    }


# ===================================================
# Montar visão completa do álbum
# ===================================================
def montar_album_usuario(db: Session, usuario) -> AlbumResponse:
    colecao = get_colecao_ativa(db)
    if not colecao:
        return AlbumResponse(
            colecao_id=0,
            nome_colecao="",
            ano=0,
            total_figurinhas=0,
            coletadas=0,
            progresso=0.0,
            figurinhas=[],
        )

    figs_colecao = listar_figurinhas_da_colecao(db, colecao.id)
    figs_usuario = listar_figurinhas_do_usuario(db, usuario.id)
    mapa_usuario = {uf.figurinha_id: uf for uf in figs_usuario}

    itens_album = []

    coletadas = 0
    for fig in figs_colecao:
        uf = mapa_usuario.get(fig.id)
        possui = uf is not None
        quantidade = uf.quantidade if uf else 0

        if possui:
            coletadas += 1

        itens_album.append(
            FigurinhaAlbum(
                id=fig.id,
                numero=fig.numero,
                nome=fig.nome,
                posicao=fig.posicao,
                time=fig.time,
                raridade=fig.raridade,
                imagem_url=fig.imagem_url,
                possui=possui,
                quantidade=quantidade,
            )
        )

    progresso = 0.0
    if colecao.total_figurinhas:
        progresso = round((coletadas / colecao.total_figurinhas) * 100, 2)

    return AlbumResponse(
        colecao_id=colecao.id,
        nome_colecao=colecao.nome,
        ano=colecao.ano,
        total_figurinhas=colecao.total_figurinhas,
        coletadas=coletadas,
        progresso=progresso,
        figurinhas=itens_album,
    )
