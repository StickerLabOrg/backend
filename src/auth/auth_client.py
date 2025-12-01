# src/auth/auth_client.py
import requests
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

AUTH_API_URL = "http://auth-api:8001"  # Nome do serviço no Docker Compose
security = HTTPBearer()


# ======================================================
# Modelo que representa o usuário autenticado
# ======================================================
class AuthUser(BaseModel):
    id: int
    nome: str
    email: str
    time_do_coracao: Optional[str] = None

    class Config:
        orm_mode = True


# ======================================================
# Função para validar token chamando o Auth API + FALLBACK
# ======================================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    Tenta validar o token chamando o Auth API.
    Caso o Auth API esteja offline OU dê erro, cai no FALLBACK
    retornando um usuário fake (id=1).
    """
    token = credentials.credentials

    # -------------------------
    # 1) Tenta acessar Auth API
    # -------------------------
    try:
        response = requests.get(
            f"{AUTH_API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        # Token inválido, expirado ou sem permissão
        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado.",
            )

        # Sucesso → tenta validar os dados
        if response.status_code == 200:
            try:
                data = response.json()
                return AuthUser(**data)
            except Exception:
                pass  # se vier lixo da API, cai no fallback

    # -------------------------
    # 2) Problemas com Auth API
    # -------------------------
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass
    except Exception:
        pass

    # -------------------------
    # 3) FALLBACK para DEMO
    # -------------------------
    return AuthUser(
        id=1,
        nome="Usuário Demo",
        email="demo@example.com",
    )
