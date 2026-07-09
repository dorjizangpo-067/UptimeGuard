from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DATABASE_URL: SecretStr
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY: int = 3600  # seconds
    JWT_REFRESH_TOKEN_EXPIRY: int = 2  # days

    REDIS_URL: str
    JTI_EXPIRY: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Setting()  # type: ignore
