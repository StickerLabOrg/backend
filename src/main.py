from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from src.colecao.router import router as colecao_router
from src.colecao.seed import seed_colecao
from src.db.session import Base, engine, get_db
from src.palpites.router import router as palpites_router
from src.partidas.router import router as partidas_router
from src.ranking.router import router as ranking_router
from src.usuario.router import router as user_router

app = FastAPI()

# ---- CORS FIX ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed_colecao(db)

app.include_router(user_router)
app.include_router(palpites_router)
app.include_router(partidas_router)
app.include_router(ranking_router)
app.include_router(colecao_router)
