from src.palpites.schema import PalpiteCreate
from src.palpites.service import service_create_palpite, service_get_palpite


def test_get_palpite(db_session):
    palpite_data = PalpiteCreate(
        user_id=1,
        partida_id=11,
        palpite="3x0"
    )

    palpite = service_create_palpite(db_session, palpite_data)

    fetched = service_get_palpite(db_session, palpite.id)

    assert fetched.id == palpite.id
