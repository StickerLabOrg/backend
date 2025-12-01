from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.colecao.router import router as colecao_router
from src.colecao.seed import seed_colecao
from src.db.session import Base, engine, get_db
from src.palpites.router import router as palpites_router
from src.partidas.router import router as partidas_router
from src.ranking.router import router as ranking_router
from src.usuario.router import router as user_router

# ---------------------------------------------------------
# Inicialização da Aplicação FastAPI
# ---------------------------------------------------------
app = FastAPI()

# ---------------------------------------------------------
# Configuração de CORS (acesso permitido ao front)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Evento de startup: cria tabelas e realiza seed inicial
# ---------------------------------------------------------
@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

    # Seed da coleção (gera figurinhas e raridades caso não existam)
    db = next(get_db())
    seed_colecao(db)


# ---------------------------------------------------------
# Rotas da aplicação
# ---------------------------------------------------------
app.include_router(user_router)
app.include_router(palpites_router)
app.include_router(partidas_router)
app.include_router(ranking_router)
app.include_router(colecao_router)
