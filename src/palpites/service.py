from sqlalchemy.orm import Session

from src.palpites.model import Palpite
from src.palpites.repository import (
    get_palpites_pendentes_da_partida,
    get_partidas_com_palpites_pendentes,
    update_palpite,
)
from src.palpites.schema import PalpiteCreate, PalpiteResponse
from src.partidas.service import get_partida_por_id
from src.usuario.models.user import User

MOEDAS_POR_ACERTO = 100


# -----------------------------
# PARSE PADRÃO DE PLACAR
# -----------------------------
def parse_placar(placar: str) -> tuple[int, int]:
    """
    Aceita formatos '2x1', '2X1', '2-1', '2 - 1'
    """
    separadores = ["x", "X", "-"]
    for sep in separadores:
        if sep in placar:
            partes = placar.split(sep)
            if len(partes) == 2:
                return int(partes[0].strip()), int(partes[1].strip())
    raise ValueError(f"Formato de placar inválido: {placar}")


# -----------------------------
# CRUD VIA REPOSITORY
# -----------------------------
def criar_palpite(db: Session, palpite_data: PalpiteCreate, usuario_id: int):
    placar = f"{palpite_data.palpite_gols_casa}x{palpite_data.palpite_gols_visitante}"

    novo = Palpite(
        usuario_id=usuario_id,
        partida_id=str(palpite_data.partida_id),
        palpite=placar,
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    return PalpiteResponse.from_model(novo)


def listar_palpites(db: Session, usuario_id: int):
    palpites = db.query(Palpite).filter(Palpite.usuario_id == usuario_id).all()
    return [PalpiteResponse.from_model(p) for p in palpites]


def editar_palpite(db, palpite_id, dados, usuario_id):
    palpite = update_palpite(db, palpite_id, dados, usuario_id)
    if palpite:
        return PalpiteResponse.from_model(palpite)


# -----------------------------
# AVALIAÇÃO VIA PLACAR REAL
# -----------------------------
def avaliar_palpites_da_partida(db: Session, partida_id: str):
    """
    Busca o resultado REAL da partida usando get_partida_por_id.
    Se a partida ainda não tiver placar (não finalizada), retorna None.
    """
    resultado = get_partida_por_id(partida_id)

    if (
        resultado is None
        or resultado.placar_casa is None
        or resultado.placar_fora is None
    ):
        # partida ainda não finalizada ou não encontrada
        return None

    palpites = get_palpites_pendentes_da_partida(db, partida_id)

    for palpite in palpites:
        try:
            g_casa, g_fora = parse_placar(palpite.palpite)
        except ValueError:
            palpite.acertou = False
            palpite.processado = True
            continue

        if g_casa == resultado.placar_casa and g_fora == resultado.placar_fora:
            palpite.acertou = True

            # adicionar moedas
            user = db.query(User).filter(User.id == palpite.usuario_id).first()
            if user:
                user.coins = (user.coins or 0) + MOEDAS_POR_ACERTO
        else:
            palpite.acertou = False

        palpite.processado = True

    db.commit()
    return palpites


# -----------------------------
# AVALIAÇÃO MANUAL (TESTE)
# -----------------------------
def avaliar_palpites_da_partida_teste(
    db: Session,
    partida_id: str,
    placar_real: str,
):
    g_casa, g_fora = parse_placar(placar_real)
    palpites = get_palpites_pendentes_da_partida(db, partida_id)

    for palpite in palpites:
        try:
            gc, gf = parse_placar(palpite.palpite)
        except ValueError:
            palpite.acertou = False
            palpite.processado = True
            continue

        palpite.acertou = gc == g_casa and gf == g_fora
        palpite.processado = True

        if palpite.acertou:
            user = db.query(User).filter(User.id == palpite.usuario_id).first()
            if user:
                user.coins = (user.coins or 0) + MOEDAS_POR_ACERTO

    db.commit()
    return {"mensagem": "OK", "processados": len(palpites)}


# -----------------------------
# PROCESSAMENTO AUTOMÁTICO
# -----------------------------
def processar_palpites_automaticamente(db: Session):
    """
    Processa automaticamente TODOS os palpites pendentes.

    Em vez de depender da lista de partidas ao vivo (que pode não
    conter mais as partidas que já terminaram), buscamos no banco
    todas as partidas que ainda possuem palpites não processados,
    e para cada uma delas chamamos `avaliar_palpites_da_partida`,
    que decide se já existe placar real ou não.

    Isso resolve o problema de partidas que já acabaram mas ainda
    não tinham sido processadas na hora em que estavam "ao vivo".
    """
    partidas_pendentes = get_partidas_com_palpites_pendentes(db)
    resultados: list[dict] = []

    for partida_id in partidas_pendentes:
        r = avaliar_palpites_da_partida(db, partida_id)
        if r:
            resultados.append(
                {
                    "partida": partida_id,
                    "processados": len(r),
                }
            )

    return resultados
