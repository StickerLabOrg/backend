from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import engine, Base
from source.colecao.view_colecao import router as colecao_router
from source.usuario.view_usuario import router as usuario_router

# Importa os modelos para que o create_all os encontre
from source.colecao import model_colecao
from source.usuario import model_usuario

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Hub do Torcedor")

# Configuração do CORS
# ... (código do CORS)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Hub do Torcedor!"}

app.include_router(colecao_router, prefix="/admin", tags=["Admin: Coleções"])
app.include_router(usuario_router, tags=["Autenticação e Usuários"])