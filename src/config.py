from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DATABASE_URL: SecretStr
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Setting()  # type: ignore
