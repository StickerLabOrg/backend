from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    nome: str
    email: EmailStr
    password: str
    time_do_coracao: str


class UserResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    time_do_coracao: str
    coins: int

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PerfilResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    time_do_coracao: str

    total_figurinhas: int
    progresso_album: float

    total_palpites: int
    taxa_acerto: float
    coins: int

    class Config:
        orm_mode = True


class ChangePasswordRequest(BaseModel):
    usuario_id: int
    senha_atual: str
    nova_senha: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    nova_senha: str
