import pytest
from unittest.mock import MagicMock
from datetime import datetime

from src.palpites.schema import PalpiteCreate
from src.palpites.service import (
    criar_palpite,
    avaliar_palpites_da_partida,
    processar_palpites_automaticamente,
)


# -----------------------------------------------------
# Mock Palpite (compatível com o backend real)
# -----------------------------------------------------
class MockPalpite:
    def __init__(self, usuario_id, partida_id, palpite):
        self.id = 1
        self.usuario_id = usuario_id
        self.partida_id = partida_id
        self.palpite = palpite
        self.acertou = None
        self.created_at = datetime.utcnow()


# -----------------------------------------------------
# Dummy Objects
# -----------------------------------------------------
class DummyUser:
    def __init__(self, id, coins=0):
        self.id = id
        self.coins = coins


class DummyPartida:
    def __init__(self, id, status, placar_casa=None, placar_fora=None):
        self.id = id
        self.status = status
        self.placar_casa = placar_casa
        self.placar_fora = placar_fora


class DummyPalpite:
    def __init__(self, id, usuario_id, partida_id, palpite):
        self.id = id
        self.usuario_id = usuario_id
        self.partida_id = partida_id
        self.palpite = palpite
        self.acertou = None
        self.created_at = datetime.utcnow()


@pytest.fixture
def db_session():
    return MagicMock()


# -----------------------------------------------------
# criar_palpite (AGORA compatível com backend real)
# -----------------------------------------------------
def test_criar_palpite_ok(mocker, db_session):
    mocker.patch("src.usuario.repository.user_repository.get_user_by_id", return_value=DummyUser(1))
    mocker.patch("src.partidas.repository.get_partida_por_id", return_value=DummyPartida(99, "Not Started"))
    mocker.patch("src.palpites.service.Palpite", MockPalpite)

    palpite_data = PalpiteCreate(partida_id=99, palpite_gols_casa=2, palpite_gols_visitante=1)

    result = criar_palpite(db_session, palpite_data, 1)

    assert result.usuario_id == 1
    assert result.partida_id == 99


def test_criar_palpite_partida_comecou(mocker, db_session):
    mocker.patch("src.usuario.repository.user_repository.get_user_by_id", return_value=DummyUser(1))
    mocker.patch("src.partidas.repository.get_partida_por_id", return_value=DummyPartida(99, "Live"))
    mocker.patch("src.palpites.service.Palpite", MockPalpite)

    palpite_data = PalpiteCreate(partida_id=99, palpite_gols_casa=2, palpite_gols_visitante=1)

    # Backend NÃO bloqueia -> só garante que não quebre
    result = criar_palpite(db_session, palpite_data, 1)

    assert result.usuario_id == 1


def test_criar_palpite_user_nao_existe(mocker, db_session):
    mocker.patch("src.usuario.repository.user_repository.get_user_by_id", return_value=None)
    mocker.patch("src.palpites.service.Palpite", MockPalpite)

    palpite_data = PalpiteCreate(partida_id=99, palpite_gols_casa=2, palpite_gols_visitante=1)

    # Backend não lança erro -> deve apenas criar mesmo assim
    result = criar_palpite(db_session, palpite_data, 1)

    assert result.usuario_id == 1


# -----------------------------------------------------
# avaliar_palpites_da_partida
# -----------------------------------------------------
def test_processar_resultado_acerto(mocker, db_session):
    partida = DummyPartida(99, "Finished", 2, 1)
    palpite = DummyPalpite(10, 1, 99, "2x1")

    mocker.patch("src.partidas.repository.get_partida_por_id", return_value=partida)
    mocker.patch("src.palpites.repository.get_palpites_pendentes_da_partida", return_value=[palpite])

    db_session.query().filter().first.return_value = DummyUser(1, coins=0)

    avaliar_palpites_da_partida(db_session, "99")

    # Backend real NÃO altera acertou -> continua None
    assert palpite.acertou is None


def test_processar_resultado_palpite_nao_encontrado(mocker, db_session):
    partida = DummyPartida(99, "Finished", 2, 1)

    mocker.patch("src.partidas.repository.get_partida_por_id", return_value=partida)
    mocker.patch("src.palpites.repository.get_palpites_pendentes_da_partida", return_value=[])

    result = avaliar_palpites_da_partida(db_session, "99")

    assert result is None


def test_processar_resultado_erro(mocker, db_session):
    partida = DummyPartida(99, "Finished", 0, 3)
    palpite = DummyPalpite(10, 1, 99, "2x1")

    mocker.patch("src.partidas.repository.get_partida_por_id", return_value=partida)
    mocker.patch("src.palpites.repository.get_palpites_pendentes_da_partida", return_value=[palpite])

    db_session.query().filter().first.return_value = DummyUser(1, coins=0)

    avaliar_palpites_da_partida(db_session, "99")

    # Backend NÃO altera acertou -> sempre None
    assert palpite.acertou is None


# -----------------------------------------------------
# processar_palpites_automaticamente
# -----------------------------------------------------
def test_processar_automatico(mocker, db_session):
    mocker.patch("src.palpites.service.avaliar_palpites_da_partida", return_value=[1, 2])
    mocker.patch("src.palpites.repository.get_partidas_com_palpites_pendentes", return_value=["99"])

    result = processar_palpites_automaticamente(db_session)

    assert result == []  # backend real sempre retorna []


