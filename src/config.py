from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Adicionar as novas variáveis da API
    THESPORTSDB_BASE_URL: str
    THESPORTSDB_API_KEY: str
    THESPORTSDB_DEFAULT_LEAGUE_ID: int
    THESPORTSDB_DEFAULT_SEASON: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
