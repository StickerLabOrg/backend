from fastapi import APIRouter
from pydantic import BaseModel

# Pydantic Schemas (para validação de dados de entrada/saída)
class ColecaoSchema(BaseModel):
    nome: str
    ano: int
    ativo: bool

    class Config:
        orm_mode = True

# Rotas da API
router = APIRouter()

@router.post("/admin/colecoes/", response_model=ColecaoSchema, status_code=201)
def criar_colecao(colecao: ColecaoSchema):
    # Lógica para chamar o controller e criar a coleção
    return colecao # Exemplo de retorno