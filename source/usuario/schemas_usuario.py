from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    nome: str
    time_do_coracao: str
    password: str

class UsuarioSchema(UsuarioBase):
    id: int
    nome: str
    moedas: int
    is_admin: bool

    class Config:
        from_attributes = True

# A classe Token foi removida daqui.