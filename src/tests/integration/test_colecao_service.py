import pytest
from sqlalchemy.orm import Session

from src.colecao.repository import listar_pacotes
from src.colecao.service import (
    abrir_pacote,
    confirmar_insercao,
    montar_album_usuario,
)
from src.colecao.models import (
    UsuarioFigurinha,
    Figurinha,
    Pacote,
    RaridadeEnum,
    Colecao,
)
from src.usuario.models.user import User


# ----------------------------------------
# FIXTURE: cria uma coleção base
# ----------------------------------------
@pytest.fixture
def colecao_base(db: Session):
    col = Colecao(
        nome="Brasileirão 2025",
        ano=2025,
        ativa=True,
        total_figurinhas=200,
    )
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


# ----------------------------------------
# Helper: criar pacote
# ----------------------------------------
def criar_pacote_base(db: Session):
    pacote = Pacote(
        nome="Pacote Teste",
        preco_moedas=100,
        quantidade_figurinhas=5,
        chances_raridade={"comum": 75, "rara": 20, "epica": 4, "lendaria": 1},
    )
    db.add(pacote)
    db.commit()
    db.refresh(pacote)
    return pacote


# ----------------------------------------
# Helper: criar figurinhas
# ----------------------------------------
def criar_figurinhas_fake(db, colecao_id: int, quantidade: int = 20):
    """
    Cria figurinhas fake para testes.
    Suporta quantidade e garante figurinhas suficientes em todas as raridades.
    """
    from src.colecao.models import Figurinha, RaridadeEnum

    raridades = [
        RaridadeEnum.comum,
        RaridadeEnum.rara,
        RaridadeEnum.epica,
        RaridadeEnum.lendaria,
    ]

    figs = []

    # Se quantidade < 4, pelo menos 1 por raridade
    qtd_base = max(quantidade // len(raridades), 1)

    numero = 1
    for rar in raridades:
        for i in range(qtd_base):
            fig = Figurinha(
                numero=numero,
                nome=f"{rar.value.capitalize()} {numero}",
                raridade=rar,
                colecao_id=colecao_id,
            )
            numero += 1
            db.add(fig)
            figs.append(fig)

    db.commit()
    return figs



# ============================================================
# TESTES
# ============================================================

def test_listar_pacotes(db: Session):
    pac = criar_pacote_base(db)
    pacotes = listar_pacotes(db)

    assert len(pacotes) >= 1
    assert pacotes[0].nome == "Pacote Teste"
    assert pacotes[0].preco_moedas == 100


def test_abrir_pacote(db: Session, colecao_base):
    usuario = db.query(User).get(1)
    usuario.coins = 500
    db.commit()

    pacote = criar_pacote_base(db)
    criar_figurinhas_fake(db, colecao_base.id)

    resposta = abrir_pacote(db, usuario, pacote.id)

    assert len(resposta["figurinhas"]) == pacote.quantidade_figurinhas
    assert resposta["novas"] > 0
    assert resposta["pacote_id_temporario"] > 0


def test_abrir_pacote_sem_moedas(db: Session, colecao_base):
    usuario = db.query(User).get(1)
    usuario.coins = 0
    db.commit()

    pacote = criar_pacote_base(db)
    criar_figurinhas_fake(db, colecao_base.id)

    with pytest.raises(ValueError):
        abrir_pacote(db, usuario, pacote.id)


def test_confirmar_insercao(db: Session, colecao_base):
    usuario = db.query(User).get(1)
    usuario.coins = 500
    db.commit()

    pacote = criar_pacote_base(db)
    criar_figurinhas_fake(db, colecao_base.id)

    abertura = abrir_pacote(db, usuario, pacote.id)
    temp_id = abertura["pacote_id_temporario"]

    resultado = confirmar_insercao(db, usuario, temp_id)

    assert resultado["novas_adicionadas"] > 0
    assert resultado["progresso_final"] >= 0


def test_montar_album(db: Session, colecao_base):
    usuario = db.get(User, 1)

    figs = criar_figurinhas_fake(db, colecao_base.id, quantidade=20)

    # adicionar 5 figurinhas ao álbum
    for i in range(5):
        db.add(
            UsuarioFigurinha(
                usuario_id=usuario.id,
                figurinha_id=figs[i].id,
                quantidade=1,
            )
        )
    db.commit()

    album = montar_album_usuario(db, usuario)

    # A coleção tem 200 slots
    assert album.total_figurinhas == 200

    # O usuário coletou somente 5
    assert album.coletadas == 5

    # Progresso baseado em 200 slots, não nos 20 criados
    assert album.progresso == round((5 / 200) * 100, 2)
