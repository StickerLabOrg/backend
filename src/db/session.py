import os

# ---------------------------------------------------
# MODO TESTE UNITÁRIO → NÃO CRIA ENGINE REAL
# ---------------------------------------------------
if os.environ.get("UNIT_TEST", "0") == "1":
    from unittest.mock import MagicMock

    Base = object  # Apenas um placeholder para permitir importações

    SessionLocal = MagicMock()

    def get_db():
        """Mock do get_db para testes unitários."""
        yield MagicMock()

# ---------------------------------------------------
# MODO NORMAL → BACKEND REAL
# ---------------------------------------------------
else:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    from src.config import settings

    Base = declarative_base()

    engine = create_engine(
        settings.DATABASE_URL,
        future=True,
        echo=False
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
