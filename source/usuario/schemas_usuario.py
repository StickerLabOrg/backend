from pydantic import BaseModel, EmailStr

# 🔹 Classe base com os campos comuns
class UsuarioBase(BaseModel):
    email: EmailStr

# 🔹 Classe usada para criação de usuário (entrada da API)
class UsuarioCreate(UsuarioBase):
    nome: str
    time_do_coracao: str
    password: str

# 🔹 Classe usada para resposta da API (saída)
class UsuarioSchema(UsuarioBase):
    id: int
    nome: str
    moedas: int
    is_admin: bool
    time_do_coracao: str
    pontos: int
    taxa_de_acerto: float

    class Config:
        orm_mode = True          # compatível com Pydantic v1
        from_attributes = True   # compatível com Pydantic v2
