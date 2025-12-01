from typing import List, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session
from sqlalchemy.sql import case

from src.palpites.model import Palpite
from src.ranking.schema import RankingItem, RankingResponse
from src.usuario.models.user import User

PONTOS_POR_ACERTO = 10


def montar_avatar(nome: str) -> str:
    """Gera o avatar com base na primeira letra do nome."""
    return nome[0].upper()


def medalha_para_posicao(posicao: int):
    """Retorna a medalha correspondente à posição."""
    return {1: "ouro", 2: "prata", 3: "bronze"}.get(posicao)


def _query_base(db: Session, filtro=None):
    """Consulta base que une usuários e palpites."""

    acertos_expr = func.sum(case((Palpite.acertou, 1), else_=0)).label("acertos")

    total_expr = func.count(Palpite.id).label("total_palpites")

    q = db.query(
        User.id,
        User.nome,
        User.coins,
        total_expr,
        acertos_expr,
    ).outerjoin(Palpite, Palpite.usuario_id == User.id)

    if filtro is not None:
        q = q.filter(filtro)

    return q.group_by(User.id, User.nome, User.coins).all()


def _montar_ranking(rows, usuario_id: Optional[int]):
    ranking: List[RankingItem] = []

    for row in rows:
        total = row.total_palpites or 0
        acertos = row.acertos or 0
        # Se o usuário tiver coins, usa como pontuação
        pontos = row.coins if row.coins is not None else acertos * PONTOS_POR_ACERTO

        precisao = (acertos / total * 100) if total > 0 else 0

        ranking.append(
            RankingItem(
                posicao=0,  # será preenchido depois
                medalha=None,
                avatar=montar_avatar(row.nome),
                nome=row.nome,
                pontos=pontos,
                precisao=round(precisao, 2),
                palpites=total,
                is_you=(row.id == usuario_id),
            )
        )

    # Ordenar por pontos
    ranking.sort(key=lambda x: x.pontos, reverse=True)

    # Atribuir posições e medalhas
    for i, item in enumerate(ranking, start=1):
        item.posicao = i
        item.medalha = medalha_para_posicao(i)

    return ranking


def ranking_geral(db: Session, usuario_id: Optional[int]):
    """Ranking total sem filtros."""
    rows = _query_base(db)
    ranking = _montar_ranking(rows, usuario_id)
    return RankingResponse(total=len(ranking), ranking=ranking)


def ranking_mensal(db: Session, usuario_id: Optional[int]):
    """Ranking considerando apenas palpites do mês atual."""

    if db.bind.dialect.name == "sqlite":
        filtro = text("strftime('%m', palpites.created_at) = strftime('%m', CURRENT_TIMESTAMP)")
    else:
        filtro = func.date_part("month", Palpite.created_at) == func.date_part("month", func.now())

    rows = _query_base(db, filtro)
    ranking = _montar_ranking(rows, usuario_id)
    return RankingResponse(total=len(ranking), ranking=ranking)


def ranking_semanal(db: Session, usuario_id: Optional[int]):
    """Ranking considerando apenas palpites da semana atual."""

    if db.bind.dialect.name == "sqlite":
        filtro = text("strftime('%W', palpites.created_at) = strftime('%W', CURRENT_TIMESTAMP)")
    else:
        filtro = func.date_part("week", Palpite.created_at) == func.date_part("week", func.now())

    rows = _query_base(db, filtro)
    ranking = _montar_ranking(rows, usuario_id)
    return RankingResponse(total=len(ranking), ranking=ranking)
