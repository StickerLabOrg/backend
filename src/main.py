from fastapi import FastAPI
from src.db.session import engine, get_db
from src.db.base import Base

# importar MODELS
from src.usuario.models.user import User
from src.palpites.model import Palpite

# importar routers
from src.usuario.router import router as user_router
from src.palpites.router import router as palpites_router
from src.partidas.router import router as partidas_router
from src.ranking.router import router as ranking_router
from src.colecao.router import router as colecao_router

# importar SEED
from src.colecao.seed import seed_colecao

app = FastAPI()

@app.on_event("startup")
def startup():
    # criar tabelas
    Base.metadata.create_all(bind=engine)

    # executar seed
    db = next(get_db())
    seed_colecao(db)

# incluir rotas
app.include_router(user_router)
app.include_router(palpites_router)
app.include_router(partidas_router)
app.include_router(ranking_router)
app.include_router(colecao_router)
