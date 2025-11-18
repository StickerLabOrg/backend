from src.usuario.service.user_service import get_password_hash, verify_password

def test_password_hashing():
    senha = "123456"
    hashed = get_password_hash(senha)
    assert verify_password(senha, hashed)
