import secrets
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True


class Config(BaseConfig):
    ENVIRONMENT: str
    DATABASE_URL: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int
    REDIS_URL: str

    class Config:
        env_file = "./.env"


config = Config()
