from sqlalchemy.orm import Session

from src.palpites.model import Palpite
from src.palpites.schema import PalpiteCreate, PalpiteUpdate


def create_palpite(db: Session, palpite_data: PalpiteCreate):
    palpite = Palpite(**palpite_data.dict())
    db.add(palpite)
    db.commit()
    db.refresh(palpite)
    return palpite


def get_palpite(db: Session, palpite_id: int):
    return db.query(Palpite).filter(Palpite.id == palpite_id).first()


def get_all_palpites(db: Session):
    return db.query(Palpite).all()


# ==============================
# PALPITES PENDENTES
# ==============================


def get_palpites_pendentes_da_partida(db: Session, partida_id: str):
    return (
        db.query(Palpite)
        .filter(
            Palpite.partida_id == partida_id,
            Palpite.processado.is_(False),
        )
        .all()
    )


def get_partidas_com_palpites_pendentes(db: Session) -> list[str]:
    """
    Retorna a lista de IDs de partidas que ainda possuem palpites
    não processados. Isso é usado pelo processamento automático
    para decidir quais partidas precisam ser avaliadas.
    """
    rows = db.query(Palpite.partida_id).filter(Palpite.processado.is_(False)).distinct().all()
    # rows vem como lista de tuplas (("2385385",), ("2385386",)...)
    return [r[0] for r in rows]


def update_palpite(db: Session, palpite_id: int, dados: PalpiteUpdate, usuario_id: int):
    palpite = (
        db.query(Palpite)
        .filter(
            Palpite.id == palpite_id,
            Palpite.usuario_id == usuario_id,
            Palpite.processado.is_(False),
        )
        .first()
    )

    if not palpite:
        return None

    # Reconstruir placar (mantém valor atual caso campo esteja vazio)
    g_casa = dados.palpite_gols_casa if dados.palpite_gols_casa is not None else int(palpite.palpite.split("x")[0])
    g_fora = (
        dados.palpite_gols_visitante if dados.palpite_gols_visitante is not None else int(palpite.palpite.split("x")[1])
    )

    palpite.palpite = f"{g_casa}x{g_fora}"

    db.commit()
    db.refresh(palpite)
    return palpite
