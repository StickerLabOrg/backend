from src.palpites.schema import PalpiteCreate
from src.palpites.service import service_create_palpite


def test_create_palpite(db_session):
    palpite_data = PalpiteCreate(
        user_id=1,
        partida_id=10,
        palpite="2x1"
    )

    palpite = service_create_palpite(db_session, palpite_data)

    assert palpite.id is not None
    assert palpite.user_id == 1
    assert palpite.partida_id == 10
    assert palpite.palpite == "2x1"
