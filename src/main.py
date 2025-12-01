# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.colecao.router import router as colecao_router
from src.colecao.seed import seed_colecao
from src.db.session import Base, engine, get_db

from src.palpites.router import router as palpites_router
from src.partidas.router import router as partidas_router
from src.ranking.router import router as ranking_router


# ---------------------------------------------------------
# Inicialização da Aplicação FastAPI
# ---------------------------------------------------------
app = FastAPI(title="Hub Torcedor API", version="1.0.0")


# ---------------------------------------------------------
# Configuração de CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Evento de startup
# ---------------------------------------------------------
@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

    # Seed inicial da coleção
    db = next(get_db())
    seed_colecao(db)


# ---------------------------------------------------------
# Rotas da aplicação
# ---------------------------------------------------------

# ⚽ Funcionalidades principais
app.include_router(palpites_router)
app.include_router(partidas_router)
app.include_router(ranking_router)
app.include_router(colecao_router)


# ---------------------------------------------------------
# Rota raiz
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"status": "Backend principal online"}
