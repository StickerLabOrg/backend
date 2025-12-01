from unittest.mock import MagicMock

import pytest

import src.usuario.service.user_service as user_service


# -----------------------------------------------------
# Dummy User para simular retorno do banco
# -----------------------------------------------------
class DummyUser:
    def __init__(self, id, nome, email, time_do_coracao, password_hash="hash", coins=0):
        self.id = id
        self.nome = nome
        self.email = email
        self.time_do_coracao = time_do_coracao
        self.password_hash = password_hash
        self.coins = coins


@pytest.fixture
def db_session():
    return MagicMock()


# -----------------------------------------------------
# register_user
# -----------------------------------------------------
def test_register_user_ok(mocker, db_session):
    data = MagicMock(
        nome="Lucas",
        email="lucas@example.com",
        password="123",
        time_do_coracao="Palmeiras",
    )

    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=None)
    mocker.patch("src.usuario.service.user_service.get_password_hash", return_value="fake_hash")

    fake_user = DummyUser(1, data.nome, data.email, data.time_do_coracao)
    mocker.patch("src.usuario.service.user_service.create_user", return_value=fake_user)

    result = user_service.register_user(db_session, data)

    assert result.id == 1
    assert result.email == "lucas@example.com"


def test_register_user_email_in_use(mocker, db_session):
    data = MagicMock(
        nome="Lucas",
        email="lucas@example.com",
        password="123",
        time_do_coracao="Palmeiras",
    )

    mocker.patch(
        "src.usuario.service.user_service.get_user_by_email",
        return_value=DummyUser(1, "Outro", "lucas@example.com", "Corinthians"),
    )

    with pytest.raises(ValueError):
        user_service.register_user(db_session, data)


# -----------------------------------------------------
# login_user
# -----------------------------------------------------
def test_login_user_ok(mocker, db_session):
    fake_user = DummyUser(1, "Lucas", "lucas@example.com", "Palmeiras", password_hash="hash")

    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.verify_password", return_value=True)
    mocker.patch("src.usuario.service.user_service.create_access_token", return_value="token123")

    result = user_service.login_user(db_session, fake_user.email, "123")

    assert result["access_token"] == "token123"


def test_login_user_invalid_password(mocker, db_session):
    fake_user = DummyUser(1, "Lucas", "lucas@example.com", "Palmeiras")

    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.verify_password", return_value=False)

    with pytest.raises(ValueError):
        user_service.login_user(db_session, fake_user.email, "errada")


def test_login_user_not_found(mocker, db_session):
    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=None)

    with pytest.raises(ValueError):
        user_service.login_user(db_session, "naoexiste@example.com", "123")


# -----------------------------------------------------
# get_user_profile
# -----------------------------------------------------
def test_get_user_profile_ok(mocker, db_session):
    fake_user = DummyUser(1, "Lucas", "lucas@example.com", "Palmeiras")

    mocker.patch("src.usuario.service.user_service.get_user_by_id", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.Palpite")

    db_session.query().filter().count.return_value = 10  # total palpites
    db_session.query().select_from().filter().scalar.return_value = 7  # acertos

    result = user_service.get_user_profile(db_session, fake_user.id)

    assert result.nome == "Lucas"
    assert result.total_palpites == 10
    assert result.taxa_acerto == 70.0


def test_get_user_profile_not_found(mocker, db_session):
    mocker.patch("src.usuario.service.user_service.get_user_by_id", return_value=None)

    result = user_service.get_user_profile(db_session, 999)

    assert result is None


# -----------------------------------------------------
# change_password
# -----------------------------------------------------
def test_change_password_ok(mocker, db_session):
    fake_user = DummyUser(
        1,
        "Lucas",
        "lucas@example.com",
        "Palmeiras",
        password_hash="old_hash",
    )

    mocker.patch("src.usuario.service.user_service.get_user_by_id", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.verify_password", return_value=True)
    mocker.patch("src.usuario.service.user_service.get_password_hash", return_value="new_hash")

    mock_update = mocker.patch("src.usuario.service.user_service.update_user_password")

    result = user_service.change_password(db_session, 1, "123", "456")

    assert result["mensagem"] == "Senha alterada com sucesso."
    mock_update.assert_called_once_with(db_session, 1, "new_hash")


def test_change_password_invalid(mocker, db_session):
    fake_user = DummyUser(1, "Lucas", "lucas@example.com", "Palmeiras")

    mocker.patch("src.usuario.service.user_service.get_user_by_id", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.verify_password", return_value=False)

    with pytest.raises(ValueError):
        user_service.change_password(db_session, 1, "errada", "nova")


# -----------------------------------------------------
# reset_password_by_email
# -----------------------------------------------------
def test_reset_password_by_email_ok(mocker, db_session):
    fake_user = DummyUser(1, "Lucas", "lucas@example.com", "Palmeiras")

    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=fake_user)
    mocker.patch("src.usuario.service.user_service.get_password_hash", return_value="new_hash")

    mock_update = mocker.patch("src.usuario.service.user_service.update_user_password")

    result = user_service.reset_password_by_email(db_session, "lucas@example.com", "nova")

    assert result["mensagem"] == "Senha redefinida com sucesso."
    mock_update.assert_called_once()


def test_reset_password_by_email_not_found(mocker, db_session):
    mocker.patch("src.usuario.service.user_service.get_user_by_email", return_value=None)

    with pytest.raises(ValueError):
        user_service.reset_password_by_email(db_session, "naoexiste@example.com", "123")
