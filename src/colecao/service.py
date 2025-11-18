import random
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.colecao.models import (
    Pacote,
    Figurinha,
    UsuarioFigurinha,
    UsuarioAlbum,
    Colecao,
    PacoteAberto
)

from src.colecao.schema import (
    AlbumResponse,
    FigurinhaAlbum
)

from src.colecao.repository import (
    criar_colecao,
    atualizar_colecao,
    deletar_colecao,
    get_colecao_by_id,
    get_colecao_ativa,
    listar_figurinhas_da_colecao,
    listar_figurinhas_do_usuario
)



# ===================================================
# Função para sortear a raridade corretamente
# ===================================================

def sortear_raridade(chances: dict[str, float]) -> str:
    r = random.random()
    acumulado = 0.0
    for raridade, chance in chances.items():
        acumulado += chance
        if r <= acumulado:
            return raridade

    return "comum"


# ===================================================
# Função principal: abrir pacote
# ===================================================

def abrir_pacote(db: Session, usuario, pacote_id: int):
    pacote = db.query(Pacote).filter(Pacote.id == pacote_id).first()

    if not pacote:
        raise ValueError("Pacote não encontrado")

    if usuario.coins < pacote.preco_moedas:
        raise ValueError("Moedas insuficientes")

    # Deduz moedas
    usuario.coins -= pacote.preco_moedas

    figurinhas = []
    raridades_contagem = {"comum": 0, "rara": 0, "epica": 0, "lendaria": 0}
    novas = 0
    repetidas = 0

    for _ in range(pacote.quantidade_figurinhas):
        raridade = sortear_raridade(pacote.chances_raridade)

        fig = (
            db.query(Figurinha)
            .filter(Figurinha.raridade == raridade)
            .order_by(func.random())
            .first()
        )

        if not fig:
            continue

        record = db.query(UsuarioFigurinha).filter(
            UsuarioFigurinha.usuario_id == usuario.id,
            UsuarioFigurinha.figurinha_id == fig.id
        ).first()

        is_new = record is None
        if is_new:
            novas += 1
        else:
            repetidas += 1

        raridades_contagem[fig.raridade.value] += 1

        figurinhas.append({
            "id": fig.id,
            "numero": fig.numero,
            "nome": fig.nome,
            "time": fig.time,
            "raridade": fig.raridade.value,
            "imagem_url": fig.imagem_url,
            "nova": is_new
        })

    # salva conteúdo temporário
    pacote_temp = PacoteAberto(
        usuario_id=usuario.id,
        conteudo=figurinhas
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
        "moedas_restantes": usuario.coins
    }


# ===================================================
# Lógica real de progresso: baseia-se em figurinhas únicas
# ===================================================

def atualizar_progresso_album(db: Session, usuario):
    colecao = db.query(Colecao).filter(Colecao.ativa == True).first()

    figurinhas_unicas = db.query(UsuarioFigurinha).filter(
        UsuarioFigurinha.usuario_id == usuario.id
    ).count()

    album = db.query(UsuarioAlbum).filter(
        UsuarioAlbum.usuario_id == usuario.id,
        UsuarioAlbum.colecao_id == colecao.id
    ).first()

    if not album:
        album = UsuarioAlbum(
            usuario_id=usuario.id,
            colecao_id=colecao.id
        )
        db.add(album)

    album.total_completas = figurinhas_unicas
    album.total_encontradas = figurinhas_unicas
    db.commit()


def calcular_progresso(db: Session, usuario) -> float:
    colecao = db.query(Colecao).filter(Colecao.ativa == True).first()
    if not colecao:
        return 0.0

    album = db.query(UsuarioAlbum).filter(
        UsuarioAlbum.usuario_id == usuario.id,
        UsuarioAlbum.colecao_id == colecao.id
    ).first()

    if not album:
        return 0.0

    progresso = (album.total_completas / colecao.total_figurinhas) * 100
    return round(progresso, 2)

def service_criar_colecao(db, data):
    return criar_colecao(db, data)

def service_atualizar_colecao(db, colecao_id, data):
    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise ValueError("Coleção não encontrada")
    return atualizar_colecao(db, colecao, data)

def service_deletar_colecao(db, colecao_id):
    colecao = get_colecao_by_id(db, colecao_id)
    if not colecao:
        raise ValueError("Coleção não encontrada")
    deletar_colecao(db, colecao)
    return True

def confirmar_insercao(db: Session, usuario, pacote_temp_id: int):
    pacote_temp = db.query(PacoteAberto).filter(
        PacoteAberto.id == pacote_temp_id,
        PacoteAberto.usuario_id == usuario.id
    ).first()

    if not pacote_temp:
        raise ValueError("Pacote temporário não encontrado")

    conteudo = pacote_temp.conteudo

    novas = 0
    repetidas = 0

    for item in conteudo:
        fig_id = item["id"]
        record = db.query(UsuarioFigurinha).filter(
            UsuarioFigurinha.usuario_id == usuario.id,
            UsuarioFigurinha.figurinha_id == fig_id
        ).first()

        if record:
            record.quantidade += 1
            repetidas += 1
        else:
            nova = UsuarioFigurinha(
                usuario_id=usuario.id,
                figurinha_id=fig_id,
                quantidade=1
            )
            db.add(nova)
            novas += 1

    atualizar_progresso_album(db, usuario)

    # apagar registro temporário
    db.delete(pacote_temp)
    db.commit()

    return {
        "novas_adicionadas": novas,
        "repetidas_incrementadas": repetidas,
        "progresso_final": calcular_progresso(db, usuario)
    }

def confirmar_insercao(db: Session, usuario, pacote_temp_id: int):
    # Busca o pacote temporário
    pacote_temp = db.query(PacoteAberto).filter(
        PacoteAberto.id == pacote_temp_id,
        PacoteAberto.usuario_id == usuario.id
    ).first()

    if not pacote_temp:
        raise ValueError("Pacote temporário não encontrado")

    conteudo = pacote_temp.conteudo

    novas = 0
    repetidas = 0

    # Processar cada figurinha
    for item in conteudo:
        fig_id = item["id"]

        record = db.query(UsuarioFigurinha).filter(
            UsuarioFigurinha.usuario_id == usuario.id,
            UsuarioFigurinha.figurinha_id == fig_id
        ).first()

        if record:
            record.quantidade += 1
            repetidas += 1
        else:
            nova = UsuarioFigurinha(
                usuario_id=usuario.id,
                figurinha_id=fig_id,
                quantidade=1
            )
            db.add(nova)
            novas += 1

    # Atualiza progresso
    atualizar_progresso_album(db, usuario)

    # Apaga o pacote temporário
    db.delete(pacote_temp)
    db.commit()

    return {
        "novas_adicionadas": novas,
        "repetidas_incrementadas": repetidas,
        "progresso_final": calcular_progresso(db, usuario)
    }
    


def montar_album_usuario(db: Session, usuario) -> AlbumResponse:
    """
    Monta a visão completa do álbum para o usuário:
    - lista TODAS as figurinhas da coleção ativa
    - marca quais ele possui
    - calcula progresso e total coletadas
    """
    colecao = get_colecao_ativa(db)
    if not colecao:
        # Se não tiver coleção ativa, você pode levantar erro ou retornar vazio
        return AlbumResponse(
            colecao_id=0,
            nome_colecao="",
            ano=0,
            total_figurinhas=0,
            coletadas=0,
            progresso=0.0,
            figurinhas=[]
        )

    # Todas as figurinhas da coleção, na ordem correta
    figs_colecao = listar_figurinhas_da_colecao(db, colecao.id)

    # Figurinhas que o usuário possui
    figs_usuario = listar_figurinhas_do_usuario(db, usuario.id)
    mapa_usuario = {uf.figurinha_id: uf for uf in figs_usuario}

    itens_album: list[FigurinhaAlbum] = []
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
        figurinhas=itens_album
    )

