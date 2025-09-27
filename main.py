from fastapi import FastAPI
from config import engine, Base
from source.colecao import view_colecao

# Comando para criar a tabela no banco de dados (se ela não existir)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Hub do Torcedor")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Hub do Torcedor!"}

# Inclui as rotas do CRUD de Coleção na API principal
app.include_router(view_colecao.router, prefix="/admin", tags=["Admin: Coleções"])