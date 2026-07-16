import ssl

import certifi
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ca_certs = ssl.get_default_verify_paths().cafile or certifi.where()


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

    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_FROM: SecretStr
    MAIL_FROM_NAME: str
    DOMAIN: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Setting()  # type: ignore

# celery
broker_url = config.REDIS_URL

result_backend = config.REDIS_URL
result_expires = 3600  # seconds

broker_use_ssl = {
    "ssl_cert_reqs": ssl.CERT_REQUIRED,
    "ssl_ca_certs": ca_certs,
}
redis_backend_use_ssl = {
    "ssl_cert_reqs": ssl.CERT_REQUIRED,
    "ssl_ca_certs": ca_certs,
}
broker_transport_options = {
    "max_retries": 5,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0.5,
}
