from src.palpites.schema import PalpiteCreate
from src.palpites.service import service_create_palpite, service_get_all_palpites


def test_get_all_palpites(db_session):
    service_create_palpite(db_session, PalpiteCreate(user_id=1, partida_id=1, palpite="1x0"))
    service_create_palpite(db_session, PalpiteCreate(user_id=2, partida_id=2, palpite="2x1"))

    palpites = service_get_all_palpites(db_session)

    assert len(palpites) >= 2
