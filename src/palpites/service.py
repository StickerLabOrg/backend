from sqlalchemy.orm import Session
from src.palpites.model import Palpite
from src.palpites.schema import PalpiteCreate, PalpiteUpdate
from src.usuario.models.user import User
from src.partidas.service import obter_resultado_partida_por_id, listar_partidas_ao_vivo
from src.palpites.repository import (
    create_palpite as repo_create,
    get_all_palpites,
    update_palpite,
    get_palpites_pendentes_da_partida
)

MOEDAS_POR_ACERTO = 10


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
# CRUD via repository
# -----------------------------
def criar_palpite(db: Session, palpite_data: PalpiteCreate):
    return repo_create(db, palpite_data)


def listar_palpites(db: Session):
    return get_all_palpites(db)


def editar_palpite(db: Session, palpite_id: int, dados: PalpiteUpdate, usuario_id: int):
    return update_palpite(db, palpite_id, dados, usuario_id)


# -----------------------------
# AVALIAÇÃO VIA PLACAR REAL
# -----------------------------
def avaliar_palpites_da_partida(db: Session, partida_id: str):
    """
    Busca o resultado REAL da partida na API V2.
    """
    resultado = obter_resultado_partida_por_id(partida_id)

    if (
        resultado is None
        or resultado.placar_casa is None
        or resultado.placar_fora is None
    ):
        return None  # partida não finalizada

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
def avaliar_palpites_da_partida_teste(db: Session, partida_id: str, placar_real: str):
    g_casa, g_fora = parse_placar(placar_real)
    palpites = get_palpites_pendentes_da_partida(db, partida_id)

    for palpite in palpites:
        try:
            gc, gf = parse_placar(palpite.palpite)
        except ValueError:
            palpite.acertou = False
            palpite.processado = True
            continue

        palpite.acertou = (gc == g_casa and gf == g_fora)
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
    lives = listar_partidas_ao_vivo()

    finalizadas = [p for p in lives if (p.minuto == "FT" or p.minuto == "Finished")]

    resultados = []

    for partida in finalizadas:
        partida_id = partida.id
        r = avaliar_palpites_da_partida(db, partida_id)
        if r:
            resultados.append({
                "partida": partida_id,
                "processados": len(r)
            })

    return resultados
