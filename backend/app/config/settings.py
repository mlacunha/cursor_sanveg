from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

# Caminho absoluto do .env (na raiz do projeto) para funcionar independente do cwd
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # Database - configure via .env (copie .env.example para .env e preencha)
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    # JWT - configure via .env
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email - configure via .env
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "SVEGPA"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    # Application
    APP_NAME: str = "SVEGPA API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False

        return value
    
    @property
    def DATABASE_URL(self) -> str:
        # Tenta pegar DATABASE_URL do .env/environment nativo (docker) se existir.
        import os
        url = os.getenv("DATABASE_URL")
        if url:
            # Garante o prefixo correto para SQLAlchemy + PostGIS
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            
            if "postgresql+psycopg2://" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg2://")
            return url
            
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    class Config:
        # Em produção (VPS/container) as variáveis vêm do ambiente do sistema.
        # Em desenvolvimento local lê do arquivo .env.
        env_file = str(_env_path) if _env_path.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
