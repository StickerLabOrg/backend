from unittest.mock import MagicMock

import src.partidas.service as service


# ----------------------------------------------------------
# get_ligas_por_pais
# ----------------------------------------------------------
def test_get_ligas_por_pais(mocker):
    mock_repo = mocker.patch("src.partidas.service.repository.get_ligas_por_pais")
    mock_repo.return_value = ["liga1", "liga2"]

    result = service.get_ligas_por_pais("Brazil")

    assert result == ["liga1", "liga2"]
    mock_repo.assert_called_once_with("Brazil")


# ----------------------------------------------------------
# get_proximas_partidas_league
# ----------------------------------------------------------
def test_get_proximas_partidas_league(mocker):
    fake_partidas = ["p1", "p2", "p3"]

    mock_repo = mocker.patch(
        "src.partidas.service.repository.get_proximas_partidas_league"
    )
    mock_repo.return_value = fake_partidas

    result = service.get_proximas_partidas_league("1234", limit=2)

    # O service aplica slice → retorna só 2
    assert result == ["p1", "p2"]
    mock_repo.assert_called_once_with("1234")


# ----------------------------------------------------------
# get_ultimos_resultados
# ----------------------------------------------------------
def test_get_ultimos_resultados(mocker):
    fake_results = ["r1", "r2", "r3"]

    mock_repo = mocker.patch(
        "src.partidas.service.repository.get_ultimos_resultados"
    )
    mock_repo.return_value = fake_results

    result = service.get_ultimos_resultados("999", limit=1)

    # O service NÃO corta a lista → retorna tudo
    assert result == fake_results
    mock_repo.assert_called_once_with("999", 1)


# ----------------------------------------------------------
# get_tabela
# ----------------------------------------------------------
def test_get_tabela(mocker):
    fake_table = ["t1", "t2"]

    mock_repo = mocker.patch("src.partidas.service.repository.get_tabela")
    mock_repo.return_value = fake_table

    result = service.get_tabela("123", "2024")

    assert result == fake_table
    mock_repo.assert_called_once_with("123", "2024")


# ----------------------------------------------------------
# get_elenco_time
# ----------------------------------------------------------
def test_get_elenco_time(mocker):
    fake_elenco = {"jogadores": []}

    mock_repo = mocker.patch(
        "src.partidas.service.repository.get_elenco_time"
    )
    mock_repo.return_value = fake_elenco

    result = service.get_elenco_time("987")

    assert result == fake_elenco
    mock_repo.assert_called_once_with("987")


# ----------------------------------------------------------
# get_partidas_ao_vivo
# ----------------------------------------------------------
def test_get_partidas_ao_vivo(mocker):
    fake_events = [
        {
            "idLeague": "999",
            "idEvent": "12",
            "strLeague": "Serie A",
            "strHomeTeam": "Palmeiras",
            "strAwayTeam": "Corinthians",
            "intHomeScore": 1,
            "intAwayScore": 0,
            "strStatus": "Live",
            "strHomeTeamBadge": "AAA",
            "strAwayTeamBadge": "BBB",
        }
    ]

    mocker.patch(
        "src.partidas.service.fetch_live_matches",
        return_value=fake_events,
    )

    result = service.get_partidas_ao_vivo("999")

    assert len(result) == 1
    assert result[0]["time_casa"] == "Palmeiras"
    assert result[0]["placar"] == "1 - 0"


# ----------------------------------------------------------
# obter_resultado_partida_por_id
# ----------------------------------------------------------
def test_obter_resultado_partida_por_id(mocker):
    fake_partida = MagicMock()

    mock_repo = mocker.patch("src.partidas.service.get_partida_por_id")
    mock_repo.return_value = fake_partida

    result = service.obter_resultado_partida_por_id("55")

    assert result == fake_partida
    mock_repo.assert_called_once_with("55")
