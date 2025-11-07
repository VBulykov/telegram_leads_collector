import os
from functools import lru_cache

from cryptography.fernet import Fernet
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthJWT(BaseModel):
    private_key_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth", "certs", "jwt-private.pem")
    public_key_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth", "certs", "jwt-public.pem")
    algorithm: str = "RS256"
    access_token_expires_minutes: int = 720


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DB_ECHO: bool

    API_ID: int
    API_HASH: str

    FERNET_KEY: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str | None

    Auth_JWT: AuthJWT = AuthJWT()

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    @property
    def cipher(self):
        return Fernet(self.FERNET_KEY.encode())

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings():
    settings = Settings()
    return settings
