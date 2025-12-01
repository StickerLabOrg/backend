from unittest.mock import MagicMock

import src.ranking.service as service


# -------------------------------------------------------
# Helpers para montar rows simulados do banco
# -------------------------------------------------------
class DummyRow:
    def __init__(self, id, nome, coins, total, acertos):
        self.id = id
        self.nome = nome
        self.coins = coins
        self.total_palpites = total
        self.acertos = acertos


# -------------------------------------------------------
# Teste da montagem do avatar
# -------------------------------------------------------
def test_montar_avatar():
    assert service.montar_avatar("Lucas") == "L"
    assert service.montar_avatar("ana") == "A"


# -------------------------------------------------------
# Teste medalhas
# -------------------------------------------------------
def test_medalha_para_posicao():
    assert service.medalha_para_posicao(1) == "ouro"
    assert service.medalha_para_posicao(2) == "prata"
    assert service.medalha_para_posicao(3) == "bronze"
    assert service.medalha_para_posicao(10) is None


# -------------------------------------------------------
# Teste montagem de ranking (função interna)
# -------------------------------------------------------
def test_montar_ranking():
    rows = [
        DummyRow(1, "Lucas", 50, 10, 7),
        DummyRow(2, "Marcos", 20, 5, 2),
    ]

    ranking = service._montar_ranking(rows, usuario_id=1)

    assert len(ranking) == 2

    # item 1
    assert ranking[0].nome == "Lucas"
    assert ranking[0].pontos == 50
    assert ranking[0].posicao == 1
    assert ranking[0].medalha == "ouro"
    assert ranking[0].is_you is True

    # item 2
    assert ranking[1].nome == "Marcos"
    assert ranking[1].posicao == 2
    assert ranking[1].medalha == "prata"


# -------------------------------------------------------
# Teste ranking geral
# -------------------------------------------------------
def test_ranking_geral(mocker):
    db = MagicMock()

    rows = [
        DummyRow(10, "Ana", 30, 10, 5),
        DummyRow(20, "João", 10, 4, 2),
    ]

    mocker.patch("src.ranking.service._query_base", return_value=rows)

    result = service.ranking_geral(db, usuario_id=20)

    assert result.total == 2
    assert result.ranking[0].nome == "Ana"
    assert result.ranking[1].is_you is True


# -------------------------------------------------------
# Teste ranking semanal
# -------------------------------------------------------
def test_ranking_semanal(mocker):
    db = MagicMock()
    db.bind.dialect.name = "sqlite"  # simula SQLite

    rows = [DummyRow(1, "Carlos", 15, 5, 3)]

    mocker.patch("src.ranking.service._query_base", return_value=rows)

    result = service.ranking_semanal(db, usuario_id=None)

    assert result.total == 1
    assert result.ranking[0].pontos == 15


# -------------------------------------------------------
# Teste ranking mensal
# -------------------------------------------------------
def test_ranking_mensal(mocker):
    db = MagicMock()
    db.bind.dialect.name = "postgresql"

    rows = [DummyRow(1, "Juliana", 80, 12, 9)]

    mocker.patch("src.ranking.service._query_base", return_value=rows)

    result = service.ranking_mensal(db, usuario_id=1)

    assert result.total == 1
    assert result.ranking[0].nome == "Juliana"
    assert result.ranking[0].is_you is True
