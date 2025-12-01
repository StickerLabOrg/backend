from unittest.mock import MagicMock

from src.colecao import service


# ------------------------------
# Dummies para simulação
# ------------------------------
class DummyUser:
    def __init__(self, id, coins):
        self.id = id
        self.coins = coins


class DummyPacote:
    def __init__(self, quantidade, preco):
        self.quantidade_figurinhas = quantidade
        self.preco_moedas = preco
        self.chances_raridade = {"comum": 100}


class DummyFigurinha:
    def __init__(self, id, nome):
        self.id = id
        self.numero = id
        self.nome = nome
        self.time = ""
        self.posicao = ""
        self.raridade = service.RaridadeEnum("comum")
        self.imagem_url = ""


class DummyPossuida:
    def __init__(self, figurinha_id, quantidade):
        self.figurinha_id = figurinha_id
        self.quantidade = quantidade


class DummyPacoteAberto:
    def __init__(self, id, usuario_id, conteudo):
        self.id = id
        self.usuario_id = usuario_id
        self.conteudo = conteudo


# =====================================================================
# 1) abrir_pacote
# =====================================================================
def test_abrir_pacote_ok(mocker):
    db = MagicMock()
    user = DummyUser(1, 50)
    pacote = DummyPacote(2, 20)

    db.query().filter().first.side_effect = [pacote, None, None, None, None]

    mocker.patch("src.colecao.service.get_colecao_ativa", return_value=MagicMock(id=1))

    dummy_fig = DummyFigurinha(1, "A")
    db.query().filter().order_by().first.return_value = dummy_fig

    mocker.patch("src.colecao.service.sortear_raridade", return_value="comum")

    mocker.patch(
        "src.colecao.service.PacoteAberto",
        lambda **kw: DummyPacoteAberto(999, kw["usuario_id"], kw["conteudo"]),
    )

    result = service.abrir_pacote(db, user, 10)

    assert result["novas"] == 2
    assert result["repetidas"] == 0
    assert len(result["figurinhas"]) == 2


# =====================================================================
# 2) confirmar_insercao
# =====================================================================
def test_confirmar_insercao(mocker):
    db = MagicMock()
    user = DummyUser(1, 0)

    pacote_temp = DummyPacoteAberto(id=99, usuario_id=1, conteudo=[{"id": 1}, {"id": 2}])

    class FakePA:
        id = 99
        usuario_id = 1
        __name__ = "PacoteAberto"

    mocker.patch("src.colecao.service.PacoteAberto", FakePA)

    def fake_query(model):
        q = MagicMock()
        if model.__name__ == "PacoteAberto":
            q.filter().first.return_value = pacote_temp
        return q

    db.query.side_effect = fake_query

    dummy_fig = DummyFigurinha(1, "A")

    mocker.patch("src.colecao.repository.buscar_figurinha", return_value=dummy_fig, create=True)
    mocker.patch("src.colecao.repository.buscar_fig_usuario", return_value=None, create=True)
    mocker.patch("src.colecao.repository.inserir_figurinha_usuario", return_value=None, create=True)

    result = service.confirmar_insercao(db, user, 99)

    assert "novas_adicionadas" in result
    assert "repetidas_incrementadas" in result
    assert "progresso_final" in result


# =====================================================================
# 3) calcular_progresso
# =====================================================================
def test_calcular_progresso(mocker):
    db = MagicMock()
    user = DummyUser(1, 0)

    colecao = MagicMock(id=1, total_figurinhas=100)

    db.query().filter().first.side_effect = [
        colecao,
        MagicMock(total_completas=50, colecao_id=1, usuario_id=1),
    ]

    p = service.calcular_progresso(db, user)

    assert p == 50.0


# =====================================================================
# 4) montar_album_usuario
# =====================================================================
def test_montar_album_usuario(mocker):
    db = MagicMock()
    user = DummyUser(1, 0)

    mocker.patch(
        "src.colecao.service.get_colecao_ativa",
        return_value=MagicMock(id=1, nome="Copa", ano=2024, total_figurinhas=2),
    )

    f1 = DummyFigurinha(1, "A")
    f2 = DummyFigurinha(2, "B")

    mocker.patch("src.colecao.service.listar_figurinhas_da_colecao", return_value=[f1, f2], create=True)
    mocker.patch(
        "src.colecao.service.listar_figurinhas_do_usuario",
        return_value=[DummyPossuida(1, 1)],
        create=True,
    )

    mocker.patch("src.colecao.service.calcular_progresso", return_value=50.0)

    album = service.montar_album_usuario(db, user)

    assert album.total_figurinhas == 2
    assert album.coletadas == 1
    assert album.progresso == 50.0

    assert len(album.figurinhas) == 2
    assert album.figurinhas[0].id == 1
    assert album.figurinhas[0].possui is True
    assert album.figurinhas[1].id == 2
    assert album.figurinhas[1].possui is False
