from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Base
import pytest

# Usar um banco de dados SQLite em memória para os testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas no banco de dados de teste
Base.metadata.create_all(bind=engine)

# Função para sobrescrever a dependência do banco de dados nos testes
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()