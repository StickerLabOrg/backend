from pydantic import BaseModel

class ColecaoBase(BaseModel):
    nome: str
    ano: int
    ativo: bool

class ColecaoCreate(ColecaoBase):
    pass

class ColecaoUpdate(ColecaoBase):
    pass

class ColecaoSchema(ColecaoBase):
    id: int

    class Config:
        from_attributes = True