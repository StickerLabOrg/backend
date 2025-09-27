from fastapi import FastAPI

app = FastAPI(title="API Hub do Torcedor")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Hub do Torcedor!"}

# Aqui você registrará as rotas (views) dos seus recursos
# from source.colecao import view_colecao
# app.include_router(view_colecao.router)